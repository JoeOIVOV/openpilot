#!/usr/bin/env python3
from typing import List, Tuple, Dict
import rtree
import math
import json
import threading
from collections import deque
import time

import cereal.messaging as messaging
from cereal import log, custom
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.conversions import Conversions as CV
from openpilot.system.hardware import PC

from openpilot.dp_ext.selfdrive.tetood.lib.map_matcher import MapMatcher, Position
from openpilot.dp_ext.selfdrive.tetood.lib.overpass_api_helper import OverpassAPIHelper
from openpilot.dp_ext.selfdrive.tetood.lib.taiwan_speed_camera_loader import TaiwanSpeedCameraLoader
from openpilot.dp_ext.selfdrive.tetood.lib.utils import calculate_bearing, haversine_distance, feature_is_ahead

RADIUS = 3500

FREQ = 5 # hz

DEBUG = True

class TeToo:
    def __init__(self):
        self.current_position = None
        self.current_bearing = None
        self.road_network = {}
        self.traffic_signals = {}

        self.index = rtree.index.Index()
        self.map_matcher = None
        self.overpass_helper = None

        self.current_way = None

        self.current_road_name = None
        self.current_max_speed = 0
        self.current_tags = {}

        self.params = Params()

        self.fetching_thread = None
        self.data_lock = threading.Lock()

        self.v_ego = 0.
        self.v_cruise = 0.
        self.cruise_enabled = False

        self.gps_history = deque(maxlen=1*FREQ)
        self.bearing_history = deque(maxlen=1*FREQ)

        self._osm = True if PC else self.params.get_bool("dp_tetoo")
        self._taiwan_speed_camera_enabled = True if PC else self.params.get_bool("dp_tetoo_speed_camera_taiwan")
        self._speed_camera_threshold = int(self.params.get_bool("dp_tetoo_speed_camera_threshold")) * 0.01

        self.osm_speed_cameras = {}
        self.tw_speed_cameras = {}

        if self._taiwan_speed_camera_enabled:
            self.tw_speed_camera_loader = TaiwanSpeedCameraLoader()
            self.tw_speed_cameras = self.tw_speed_camera_loader.load_speed_cameras()
            if not self._osm:
                self._build_road_network()

        self.prefetched_data = None
        self.last_fetch_position = None
        if self._osm:
            last_data = self.params.get("dp_tetoo_data")
            if last_data is not None and last_data != "":
                self.prefetched_data = json.loads(last_data)
                self.map_matcher = MapMatcher(self.prefetched_data)
                self._build_road_network()

                last_pos = self.params.get("dp_tetoo_gps")
                if last_pos is not None and last_pos != "":
                    self.last_fetch_position = json.loads(last_pos)

    def update_position(self): #, lat: float, lon: float):
        self._check_and_fetch_data()

        self._map_match()
        return self._get_road_info()

    def _check_and_fetch_data(self):
        if self._osm and not self.last_fetch_position or haversine_distance(self.current_position, self.last_fetch_position) > RADIUS - self._boundary_offset():
            self._fetch_data()

    def _boundary_offset(self):
        """reduce boundary at high speed"""
        return 300 if self.v_ego < 16.67 else 600

    def _fetch_data(self):
        def fetch():
            overpass_helper = OverpassAPIHelper()
            self.prefetched_data = overpass_helper.fetch_data(self.current_position[0], self.current_position[1], RADIUS, self.v_ego > 23)
            if self.prefetched_data is not None:
                self._build_road_network()
                self.last_fetch_position = self.current_position
                self.params.put_nonblocking("dp_tetoo_gps", json.dumps(self.last_fetch_position))
                self.params.put_nonblocking("dp_tetoo_data", json.dumps(self.prefetched_data, ensure_ascii=False))

                with self.data_lock:
                    self.map_matcher = MapMatcher(self.prefetched_data)

        if self.fetching_thread is not None and self.fetching_thread.is_alive():
            return
        self.fetching_thread = threading.Thread(target=fetch)
        self.fetching_thread.start()

    def _build_road_network(self):
        new_road_network = {}
        new_index = rtree.index.Index()
        self.traffic_signals = {}
        self.osm_speed_cameras = {}

        if self._osm and self.prefetched_data:
            for element in self.prefetched_data['elements']:
                if element['type'] == 'way':
                    way_id = element['id']
                    new_road_network[way_id] = {
                        'nodes': element['nodes'],
                        'tags': element.get('tags', {})
                    }
                elif element['type'] == 'node':
                    node_id = element['id']
                    lat, lon = element['lat'], element['lon']
                    new_index.insert(node_id, (lon, lat, lon, lat))
                    new_road_network[node_id] = {'lat': lat, 'lon': lon}
                    tags = element.get('tags', {})
                    if tags.get('highway') == 'traffic_signals':
                        self.traffic_signals[node_id] = {'lat': lat, 'lon': lon, 'tags': tags}
                    elif 'highway' in tags and tags['highway'] == 'speed_camera':
                        self.osm_speed_cameras[node_id] = {'lat': lat, 'lon': lon, 'tags': tags}
                    elif 'enforcement' in tags and tags['enforcement'] == 'maxspeed':
                        self.osm_speed_cameras[node_id] = {'lat': lat, 'lon': lon, 'tags': tags}

            # Add traffic signals to the index
            for node_id, node_data in self.traffic_signals.items():
                new_index.insert(node_id, (node_data['lon'], node_data['lat'], node_data['lon'], node_data['lat']))

            # Add OSM speed cameras to the index
            for camera_id, camera_data in self.osm_speed_cameras.items():
                new_index.insert(camera_id, (camera_data['lon'], camera_data['lat'], camera_data['lon'], camera_data['lat']))

        # Add Taiwan speed cameras to the index
        if self._taiwan_speed_camera_enabled:
            for camera_id, camera_data in self.tw_speed_cameras.items():
                new_index.insert(camera_id, (camera_data['lon'], camera_data['lat'], camera_data['lon'], camera_data['lat']))

        with self.data_lock:
            self.road_network = new_road_network
            self.index = new_index

    def _map_match(self):
        if len(self.gps_history) < 1*FREQ:
            return

        if self.map_matcher is None:
            return

        self.current_way = self.map_matcher.update_position(Position(
            lat=self.current_position[0],
            lon=self.current_position[1],
            bearing=self.current_position[2],
            speed=self.current_position[3],
            turn_signal=self.current_position[4],
        ), time.time())

    def _get_road_info(self):
        if self.current_way is None:
            return {
                'id': None,
                'name': self.current_road_name,
                'maxspeed': self.current_max_speed,
                'tags': self.current_tags,
                'confidence': 0.0
            }
        way_id = self.current_way.way.id
        new_road_name = self.current_way.way.name
        new_tags = self.current_way.way.tags
        new_max_speed = self.current_way.way.tags.get("maxspeed", '0')

        # Only update if the new name is different
        if new_road_name and new_road_name != self.current_road_name:
            self.current_road_name = new_road_name
            self.current_max_speed = new_max_speed
            self.current_tags = new_tags

        return {
            'id': way_id,
            'name': self.current_road_name,
            'maxspeed': self.current_max_speed,
            'tags': self.current_tags,
            # 'confidence': self.current_way_confidence
        }

    def _check_feature_ahead(self, feature_type: str, max_distance: float, max_distance_in_parallel: float) -> Tuple[bool, float, Dict, str]:
        if self.current_position is None or self.current_bearing is None:
            return False, float('inf'), {}, ""

        current_lat, current_lon, current_bearing, current_speed, current_turn_signal = self.current_position
        closest_feature_distance = float('inf')
        closest_feature_info = {}
        closest_feature_id = ""

        # Define a bounding box for the spatial query
        search_distance = max_distance / 111000  # Convert meters to degrees (approximate)
        bbox = (
            current_lon - search_distance,
            current_lat - search_distance,
            current_lon + search_distance,
            current_lat + search_distance
        )

        # Query the rtree index for nearby features
        nearby_features = list(self.index.intersection(bbox))

        for feature_id in nearby_features:
            # Check if this feature is of the correct type
            if feature_type == custom.TeToo.FeatureType.trafficSignal and feature_id not in self.traffic_signals:
                continue
            if feature_type == custom.TeToo.FeatureType.speedCamera:
                if feature_id not in self.osm_speed_cameras and feature_id not in self.tw_speed_cameras:
                    continue

            if feature_type == custom.TeToo.FeatureType.trafficSignal:
                feature_data = self.traffic_signals.get(feature_id)
            elif feature_type == custom.TeToo.FeatureType.speedCamera:
                feature_data = self.osm_speed_cameras.get(feature_id) or self.tw_speed_cameras.get(feature_id)

            if not feature_data:
                continue

            feature_lat, feature_lon = feature_data['lat'], feature_data['lon']

            feature_point = (feature_lat, feature_lon)

            distance = haversine_distance(self.current_position, feature_point)

            # Skip features beyond the maximum look-ahead distance
            if distance > max_distance:
                continue

            bearing = calculate_bearing(self.current_position, (feature_lat, feature_lon))

            # Check if the feature is ahead based on bearing
            if feature_is_ahead(self.current_bearing, bearing, 20.) and distance < closest_feature_distance:
                closest_feature_distance = distance
                closest_feature_info = feature_data
                closest_feature_id = feature_id

        return bool(closest_feature_info), closest_feature_distance, closest_feature_info, closest_feature_id

    def check_traffic_signal_ahead(self) -> Tuple[bool, float, Dict, str]:
        MAX_TRAFFIC_SIGNAL_DISTANCE = 100  # meters
        MAX_DISTANCE_IN_PARALLEL = 15
        return self._check_feature_ahead(custom.TeToo.FeatureType.trafficSignal, MAX_TRAFFIC_SIGNAL_DISTANCE, MAX_DISTANCE_IN_PARALLEL)

    def should_warn_speed_camera(self, distance: float, speed_limit: float, road_speed_limit: float = 0.):
        # If we don't know the speed limit or we don't have a threshold set, warn anyway
        if speed_limit is None or self._speed_camera_threshold == 0:
            return True

        speed_limit = float(speed_limit)
        should_warn = False

        threshold = 1 + self._speed_camera_threshold

        # when we have v_cruise set
        if not should_warn and self.v_cruise > 0.:
            speed_limit = float(speed_limit)
            lower_bound = math.floor(self.v_cruise / threshold)
            upper_bound = math.ceil(self.v_cruise * threshold)
            should_warn = lower_bound <= speed_limit <= upper_bound

        # when the current road has a speed limit
        if not should_warn and road_speed_limit > 0.:
            road_lower_bound = math.floor(road_speed_limit / threshold)
            road_upper_bound = math.ceil(road_speed_limit * threshold)
            should_warn = road_lower_bound <= speed_limit <= road_upper_bound

        # use current speed
        if not should_warn:
            v_ego_kph = self.v_ego * CV.MS_TO_KPH
            v_lower_bound = math.floor(v_ego_kph / threshold)
            v_upper_bound = math.ceil(v_ego_kph * threshold)
            should_warn = v_lower_bound <= speed_limit <= v_upper_bound

        return should_warn

    def check_speed_camera_ahead(self) -> Tuple[bool, float, Dict, str]:
        MAX_SPEED_CAMERA_DISTANCE = 1000  # meters
        MAX_DISTANCE_IN_PARALLEL = 30
        ahead, distance, info, id = self._check_feature_ahead(custom.TeToo.FeatureType.speedCamera, MAX_SPEED_CAMERA_DISTANCE, MAX_DISTANCE_IN_PARALLEL)

        if ahead:
            maxspeed = info.get('tags', {}).get('maxspeed')
            if maxspeed:
                info['maxspeed'] = maxspeed

        return ahead, distance, info, id

    def _get_feature(self, type, func, display_tags=False):
        ahead, distance, info, id = func()
        if not ahead:
            return {}
        feature = {
            'id': str(id),
            'type': type,
            'lat': float(info['lat']),
            'lon': float(info['lon']),
            'distance': float(distance),
        }
        if display_tags:
            feature['tags'] = json.dumps(info['tags'], ensure_ascii=False)
        return feature

    def tetoo_thread(self):
        sm = messaging.SubMaster(['liveLocationKalman', 'carState', 'controlsState'])
        pm = messaging.PubMaster(['teToo'])
        te_too_dat_prev = {}
        rk = Ratekeeper(FREQ)
        lat = 0.
        lon = 0.
        bearing = 0.
        while True:
            sm.update()
            location = sm['liveLocationKalman']
            localizer_valid = (location.status == log.LiveLocationKalman.Status.valid) and location.positionGeodetic.valid

            # Update GPS and bearing history at 20 Hz
            if localizer_valid:
                lat = location.positionGeodetic.value[0]
                lon = location.positionGeodetic.value[1]
                bearing = math.degrees(location.calibratedOrientationNED.value[2])

                self.v_ego = sm['carState'].vEgo
                self.cruise_enabled = sm['carState'].cruiseState.enabled

                # Update vCruise
                self.v_cruise = sm['controlsState'].vCruise

                # Update GPS history
                if self.v_ego >= 2.6:
                  self.gps_history.append((lat, lon, bearing, self.v_ego))
                  self.bearing_history.append(bearing)

            use_prev = not localizer_valid or (localizer_valid and self.v_ego < 2.6)

            dat = messaging.new_message('teToo', valid=True)
            if use_prev:
                dat.teToo = te_too_dat_prev
            else:
                dat.teToo.lat = float(lat)
                dat.teToo.lon = float(lon)
                dat.teToo.bearing = float(bearing)
                road_maxspeed = 0.

                blinker_state = 'left' if sm['carState'].leftBlinker else 'right' if sm['carState'].rightBlinker else None
                self.current_position = (lat, lon, bearing, self.v_ego, blinker_state)
                self.current_bearing = bearing

                if self._osm:
                    road_info = self.update_position() #(lat, lon)
                    dat.teToo.name = str("" if road_info['name'] is None else road_info['name'])
                    dat.teToo.maxspeed = float(road_info['maxspeed'])
                    road_maxspeed = dat.teToo.maxspeed

                features = []
                # disable for now
                # if self._osm:
                #     traffic_signal_ahead = self._get_feature(custom.TeToo.FeatureType.trafficSignal, self.check_traffic_signal_ahead)
                #     if traffic_signal_ahead:
                #         features.append(traffic_signal_ahead)

                speed_camera_ahead = self._get_feature(custom.TeToo.FeatureType.speedCamera, self.check_speed_camera_ahead, True)
                if speed_camera_ahead:
                    tags = speed_camera_ahead.get('tags', None)
                    should_show = True
                    if tags:
                        maxspeed = json.loads(tags).get('maxspeed', None)
                        should_show = self.should_warn_speed_camera(speed_camera_ahead['distance'], maxspeed, road_maxspeed)
                    if should_show:
                        features.append(speed_camera_ahead)
                dat.teToo.nearestFeatures = features

            dat.teToo.updatingData = self._osm and (self.fetching_thread is not None and self.fetching_thread.is_alive())
            pm.send('teToo', dat)
            te_too_dat_prev = dat.teToo

            rk.keep_time()

def main():
    tetoo = TeToo()
    tetoo.tetoo_thread()

if __name__ == "__main__":
    main()
