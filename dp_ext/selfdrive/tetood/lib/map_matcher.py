import math
from typing import List, Dict, Tuple, Optional, Deque
from rtree import index
import logging
from functools import lru_cache
from collections import deque
from dataclasses import dataclass
import numpy as np

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
TO_RADIANS = math.pi / 180.0
EARTH_RADIUS = 6371000  # Earth radius in meters
PADDING = 100  # meters
LANE_WIDTH = 3.7  # meters
MIN_WAY_DIST = 500  # meters
MAX_DISTANCE = 25  # meters, maximum distance to consider a way as matching
SEARCH_RADIUS = 50  # meters

class Coordinates:
    __slots__ = ['lat', 'lon']
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
        return isinstance(other, Coordinates) and self.lat == other.lat and self.lon == other.lon

    def __hash__(self):
        return hash((self.lat, self.lon))

class Position:
    __slots__ = ['lat', 'lon', 'bearing', 'speed', 'turn_signal']
    def __init__(self, lat: float, lon: float, bearing: float, speed: float, turn_signal: Optional[str] = None):
        self.lat = lat
        self.lon = lon
        self.bearing = bearing
        self.speed = speed  # Speed in meters per second
        self.turn_signal = turn_signal  # 'left', 'right', or None

    @property
    def pos(self):
        return (self.lat, self.lon, self.bearing, self.speed, self.turn_signal)

@dataclass
class OnWayResult:
    on_way: bool
    distance: float
    is_forward: bool

@dataclass
class CurrentWay:
    way: 'Way'
    distance: float
    on_way: OnWayResult
    start_position: Coordinates
    end_position: Coordinates
    confidence: float

@dataclass
class NextWayResult:
    way: 'Way'
    is_forward: bool
    start_position: Coordinates
    end_position: Coordinates

class Way:
    def __init__(self, id: int, nodes: List[Coordinates], tags: Dict[str, str]):
        self.id = id
        self.nodes = nodes
        self.tags = tags
        self._bbox = self._calculate_bbox()

    def _calculate_bbox(self):
        lats = [node.lat for node in self.nodes]
        lons = [node.lon for node in self.nodes]
        return (min(lats), min(lons), max(lats), max(lons))

    @property
    def name(self):
        # some road doesnt have name, use ID instead
        return self.tags.get('name', self.id)

    @property
    def ref(self):
        return self.tags.get('ref', '')

    @property
    def oneway(self):
        return self.tags.get('oneway', 'no').lower() == 'yes'

    @property
    def lanes(self):
        return int(self.tags.get('lanes', '2'))

    @property
    def highway_type(self):
        return self.tags.get('highway', '')

    @property
    def is_highway(self):
        highway_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary']
        return self.highway_type in highway_types

    @property
    def bridge(self):
        return self.tags.get('bridge', 'no').lower() == 'yes'

    @property
    def tunnel(self):
        return self.tags.get('tunnel', 'no').lower() == 'yes'

    @property
    def layer(self):
        return int(self.tags.get('layer', '0'))

class MapMatcher:
    def __init__(self, road_network: Dict):
        self.ways = self._load_ways(road_network)
        self.rtree = self._build_rtree()
        self.current_way = None
        self.position_history = deque(maxlen=10)
        self.way_history = deque(maxlen=10)
        self.last_switch_time = 0
        self.switch_cooldown = 5  # Seconds to wait before allowing another switch
        self.current_layer = 0
        self.way_bearings = {}  # Cache for way bearings

    def _load_ways(self, road_network: Dict) -> Dict[int, Way]:
        ways = {}
        nodes = {}
        for element in road_network['elements']:
            if element['type'] == 'node':
                nodes[element['id']] = Coordinates(element['lat'], element['lon'])
            elif element['type'] == 'way':
                way_nodes = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
                if len(way_nodes) >= 2:
                    ways[element['id']] = Way(element['id'], way_nodes, element.get('tags', {}))
        logger.info(f"Loaded {len(ways)} ways")
        return ways

    def _build_rtree(self):
        idx = index.Index()
        for way_id, way in self.ways.items():
            bbox = way._bbox
            idx.insert(way_id, (bbox[1], bbox[0], bbox[3], bbox[2]))  # Swap lat and lon
        logger.info("R-tree index built")
        return idx

    def _get_nearby_ways(self, pos: Position) -> List[Way]:
        lat_change = SEARCH_RADIUS / (EARTH_RADIUS * TO_RADIANS)
        lon_change = SEARCH_RADIUS / (EARTH_RADIUS * TO_RADIANS * math.cos(math.radians(pos.lat)))

        search_bbox = (pos.lon - lon_change, pos.lat - lat_change,
                       pos.lon + lon_change, pos.lat + lat_change)

        nearby_way_ids = list(self.rtree.intersection(search_bbox))
        return [self.ways[way_id] for way_id in nearby_way_ids]

    def _get_candidate_ways(self, nearby_ways: List[Way], pos: Position) -> List[Tuple[Way, OnWayResult]]:
        return [(way, self.on_way(way, pos)) for way in nearby_ways if self.on_way(way, pos).on_way]

    def _are_ways_connected(self, way1: Way, way2: Way) -> bool:
        return any(node in way2.nodes for node in [way1.nodes[0], way1.nodes[-1]])

    def _select_best_match(self, candidates: List[Tuple[Way, OnWayResult]], pos: Position, timestamp: float) -> Optional[Tuple[Way, OnWayResult, float]]:
        if not candidates:
            return None

        if len(candidates) == 1:
            way, on_way_result = candidates[0]
            return (way, on_way_result, self._calculate_confidence(way, on_way_result, pos))

        scored_candidates = [(way, on_way_result, self._score_candidate(way, on_way_result, pos))
                             for way, on_way_result in candidates]

        best_match = max(scored_candidates, key=lambda x: x[2])
        best_way, best_on_way_result, best_score = best_match

        if self._is_at_intersection(candidates):
            return self._handle_intersection(scored_candidates, pos)

        # Implement snapping logic
        if self.current_way and self.current_way.way.id != best_way.id:
            time_since_last_switch = timestamp - self.last_switch_time
            if time_since_last_switch < self.switch_cooldown:
                current_way_candidate = next((c for c in scored_candidates if c[0].id == self.current_way.way.id), None)
                if current_way_candidate:
                    current_way, current_on_way_result, current_score = current_way_candidate
                    if current_score > best_score * 0.8:  # Allow some tolerance
                        return (current_way, current_on_way_result, self._calculate_confidence(current_way, current_on_way_result, pos))
            else:
                self.last_switch_time = timestamp

        return (best_way, best_on_way_result, self._calculate_confidence(best_way, best_on_way_result, pos))

    def _score_candidate(self, way: Way, on_way_result: OnWayResult, pos: Position) -> float:
        score = 0

        logger.debug(f"{way.name} ({way.id})")
        logger.debug(f"{pos.pos}")
        logger.debug(f"{way.tags}")
        # Distance score
        distance_score = self._score_distance(on_way_result.distance)
        score += distance_score
        logger.debug(f"distance_score: {distance_score}")

        # Continuity score (heavily weighted)
        continuity_score = self._score_continuity(way) * 2  # Double the weight
        score += continuity_score
        logger.debug(f"continuity_score: {continuity_score}")

        # Trajectory score
        trajectory_score = self._score_trajectory(pos)
        score += trajectory_score
        logger.debug(f"trajectory_score: {trajectory_score}")

        # Speed score
        speed_score = self._score_speed(pos.speed)
        score += speed_score
        logger.debug(f"speed_score: {speed_score}")

        # Historical matches score
        historical_score = self._score_historical_matches(way)
        score += historical_score
        logger.debug(f"historical_score: {historical_score}")

        # Turn signals score
        turn_signals_score = self._score_turn_signals(way, pos)
        score += turn_signals_score
        logger.debug(f"turn_signals_score: {turn_signals_score}")

        # Layer difference score
        layer_score = self._score_layer_difference(way) * 2  # Double the weight
        score += layer_score
        logger.debug(f"layer_score: {layer_score}")

        # One-way score
        one_way_score = self._score_one_way(way, on_way_result)
        score += one_way_score
        logger.debug(f"one_way_score: {one_way_score}")

        # Connectivity score
        connectivity_score = self._score_connectivity(way) * 2  # Double the weight
        score += connectivity_score
        logger.debug(f"connectivity_score: {connectivity_score}")
        logger.debug(f"total score: {score}")

        return score

    def _score_distance(self, distance: float) -> float:
        return 100 - distance

    def _score_continuity(self, way: Way) -> float:
        return 50 if self.current_way and way.id == self.current_way.way.id else -25  # Penalize switches

    def _score_layer_difference(self, way: Way) -> float:
        if not self.current_way:
            return 0
        layer_diff = abs(int(way.tags.get('layer', '0')) - int(self.current_way.way.tags.get('layer', '0')))
        return -20 * layer_diff  # Penalize layer differences

    def _score_connectivity(self, way: Way) -> float:
        if not self.current_way:
            return 0
        if self._are_ways_connected(self.current_way.way, way):
            return 50
        return -50  # Penalize non-connected ways

    def _score_trajectory(self, pos: Position) -> float:
        if len(self.position_history) < 2:
            return 0
        prev_pos = self.position_history[-1]
        expected_bearing = self._calculate_bearing(
            Coordinates(prev_pos.lat, prev_pos.lon),
            Coordinates(pos.lat, pos.lon)
        )
        bearing_diff = abs(expected_bearing - pos.bearing)
        return -min(bearing_diff, 360 - bearing_diff)

    def _score_speed(self, speed: float) -> float:
        return 20 if speed > 8.33 else (-20 if speed < 1.39 else 0)

    def _score_historical_matches(self, way: Way) -> float:
        return 30 if way in self.way_history else 0

    def _score_turn_signals(self, way: Way, pos: Position) -> float:
        if not pos.turn_signal or not way.is_highway:
            return 0
        if self.current_way:
            parallel_score = self._score_parallel_ways(self.current_way.way, way)
            if parallel_score > 0:
                return 40
        way_bearing = self._calculate_bearing(way.nodes[0], way.nodes[-1])
        return 20 if (pos.turn_signal == 'left' and way_bearing < pos.bearing) or \
                     (pos.turn_signal == 'right' and way_bearing > pos.bearing) else 0

    def _score_one_way(self, way: Way, on_way_result: OnWayResult) -> float:
        return -100 if way.oneway and not on_way_result.is_forward else 0

    def _is_at_intersection(self, candidates: List[Tuple[Way, OnWayResult]]) -> bool:
        return len(candidates) > 2

    def _handle_intersection(self, scored_candidates: List[Tuple[Way, OnWayResult, float]], pos: Position) -> Tuple[Way, OnWayResult, float]:
        # Implement more sophisticated intersection handling logic here
        # For now, we'll just return the highest scored candidate
        return max(scored_candidates, key=lambda x: x[2])

    def _calculate_confidence(self, way: Way, on_way_result: OnWayResult, pos: Position) -> float:
        # Implement a confidence calculation based on various factors
        # This is a simple example; you might want to develop a more sophisticated model
        base_confidence = 1.0 - (on_way_result.distance / MAX_DISTANCE)
        trajectory_confidence = 1.0 if len(self.position_history) < 2 else \
            1.0 - min(abs(self._calculate_bearing(self.position_history[-1], pos) - pos.bearing) / 180.0, 1.0)
        return (base_confidence + trajectory_confidence) / 2

    def update_position(self, pos: Position, timestamp: float) -> Optional[CurrentWay]:
        logger.debug(f"Updating position: lat={pos.lat}, lon={pos.lon}, bearing={pos.bearing}, speed={pos.speed}, turn_signal={pos.turn_signal}")

        nearby_ways = self._get_nearby_ways(pos)
        candidate_ways = self._get_candidate_ways(nearby_ways, pos)
        best_match = self._select_best_match(candidate_ways, pos, timestamp)

        if best_match:
            way, on_way_result, confidence = best_match
            logger.info(f"Matched to way: {way.id} with confidence {confidence:.2f}")
            self.position_history.append(pos)
            self.way_history.append(way)
            new_current_way = self._update_current_way(pos, way, on_way_result, confidence)

            # Add a check to ensure current_way is not None
            if new_current_way is not None:
                self.current_way = new_current_way
                return self.current_way
            else:
                logger.warning("_update_current_way returned None. Keeping previous current_way.")
                return self.current_way

        logger.warning("No matching way found. Keeping previous current_way.")
        return self.current_way  # Return the previous current_way instead of None

    def on_way(self, way: Way, pos: Position) -> OnWayResult:
        distance = self._distance_to_way(pos.lat, pos.lon, way.id)

        max_dist = 5 + way.lanes * LANE_WIDTH

        if distance < max_dist:
            is_forward = self._is_forward(way.id, pos.bearing)
            if not is_forward and way.oneway:
                return OnWayResult(False, distance, is_forward)
            return OnWayResult(True, distance, is_forward)

        return OnWayResult(False, distance, False)

    @lru_cache(maxsize=1024)
    def _distance_to_way(self, pos_lat: float, pos_lon: float, way_id: int) -> float:
        way = self.ways[way_id]
        return np.min([self._point_to_line_distance(pos_lat, pos_lon, start.lat, start.lon, end.lat, end.lon)
                       for start, end in zip(way.nodes, way.nodes[1:])])

    @staticmethod
    @lru_cache(maxsize=1024)
    def _point_to_line_distance(px, py, x1, y1, x2, y2):
        px, py, x1, y1, x2, y2 = map(math.radians, [px, py, x1, y1, x2, y2])

        line_length = MapMatcher._haversine_distance(y1, x1, y2, x2)
        if line_length == 0:
            return MapMatcher._haversine_distance(py, px, y1, x1)

        a = MapMatcher._haversine_distance(py, px, y1, x1)
        b = MapMatcher._haversine_distance(py, px, y2, x2)
        c = line_length

        s = (a + b + c) / 2
        area = math.sqrt(abs(s * (s-a) * (s-b) * (s-c)))

        height = 2 * area / c

        return height

    @staticmethod
    @lru_cache(maxsize=1024)
    def _haversine_distance(lat1, lon1, lat2, lon2):
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return EARTH_RADIUS * c

    def _is_forward(self, way_id: int, bearing: float) -> bool:
        if way_id not in self.way_bearings:
            way = self.ways[way_id]
            self.way_bearings[way_id] = self._calculate_bearing(way.nodes[0], way.nodes[-1])

        way_bearing = self.way_bearings[way_id]
        bearing_diff = abs(way_bearing - bearing)
        is_forward = bearing_diff < 90 or bearing_diff > 270
        logger.debug(f"Way {way_id}: bearing {way_bearing}, vehicle bearing {bearing}, is_forward: {is_forward}")
        return is_forward

    @staticmethod
    @lru_cache(maxsize=1024)
    def _calculate_bearing(start: Coordinates, end: Coordinates) -> float:
        y = np.sin(np.radians(end.lon - start.lon)) * np.cos(np.radians(end.lat))
        x = np.cos(np.radians(start.lat)) * np.sin(np.radians(end.lat)) - \
            np.sin(np.radians(start.lat)) * np.cos(np.radians(end.lat)) * np.cos(np.radians(end.lon - start.lon))
        bearing = np.arctan2(y, x)
        return (np.degrees(bearing) + 360) % 360

    def _update_current_way(self, pos: Position, way: Way, on_way: OnWayResult, confidence: float) -> Optional[CurrentWay]:
        try:
            start, end = self._get_way_start_end(way, on_way.is_forward)
            self.current_layer = int(way.tags.get('layer', '0'))
            return CurrentWay(way, on_way.distance, on_way, start, end, confidence)
        except Exception as e:
            logger.error(f"Error in _update_current_way: {str(e)}")
            return None  # Return None if there's an error, but log it

    @staticmethod
    def _get_way_start_end(way: Way, is_forward: bool) -> Tuple[Coordinates, Coordinates]:
        return (way.nodes[0], way.nodes[-1]) if is_forward else (way.nodes[-1], way.nodes[0])

    def next_ways(self, pos: Position, current_way: CurrentWay, is_forward: bool) -> List[NextWayResult]:
        next_ways = []
        dist = 0.0
        way = current_way.way
        forward = is_forward
        start_pos = pos

        while dist < MIN_WAY_DIST:
            d = self._distance_to_end_of_way(start_pos, way, forward)
            if d <= 0:
                break
            dist += d
            nw = self._next_way(way, forward)
            if nw is None:
                break
            next_ways.append(nw)
            way = nw.way
            start_pos = Position(nw.start_position.lat, nw.start_position.lon, 0, 0)
            forward = nw.is_forward

        if not next_ways:
            nw = self._next_way(current_way.way, is_forward)
            if nw:
                next_ways.append(nw)

        return next_ways

    def _distance_to_end_of_way(self, pos: Position, way: Way, is_forward: bool) -> float:
        nodes = way.nodes if is_forward else list(reversed(way.nodes))
        return np.sum([self._haversine_distance(prev.lat, prev.lon, curr.lat, curr.lon)
                       for prev, curr in zip(nodes, nodes[1:])])

    def _next_way(self, way: Way, is_forward: bool) -> Optional[NextWayResult]:
        match_node = way.nodes[-1] if is_forward else way.nodes[0]
        matching_ways = self._matching_ways(way, match_node)

        if not matching_ways:
            return None

        for mway in matching_ways:
            if mway.name == way.name or mway.ref == way.ref:
                next_is_forward = self._next_is_forward(mway, match_node)
                if not next_is_forward and mway.oneway:
                    continue
                start, end = self._get_way_start_end(mway, next_is_forward)
                return NextWayResult(mway, next_is_forward, start, end)

        min_curv_way = min(matching_ways, key=lambda w: self._get_curvature(way, w, match_node))
        next_is_forward = self._next_is_forward(min_curv_way, match_node)
        start, end = self._get_way_start_end(min_curv_way, next_is_forward)
        return NextWayResult(min_curv_way, next_is_forward, start, end)

    def _matching_ways(self, current_way: Way, match_node: Coordinates) -> List[Way]:
        return [way for way in self.ways.values()
                if way.id != current_way.id and
                (way.nodes[0] == match_node or way.nodes[-1] == match_node)]

    @staticmethod
    def _next_is_forward(next_way: Way, match_node: Coordinates) -> bool:
        return next_way.nodes[0] == match_node

    @staticmethod
    def _get_curvature(way1: Way, way2: Way, match_node: Coordinates) -> float:
        if len(way1.nodes) < 2 or len(way2.nodes) < 2:
            return float('inf')

        node1 = way1.nodes[-2] if way1.nodes[-1] == match_node else way1.nodes[-1]
        node2 = way2.nodes[1] if way2.nodes[0] == match_node else way2.nodes[-2]

        angle1 = MapMatcher._calculate_bearing(node1, match_node)
        angle2 = MapMatcher._calculate_bearing(match_node, node2)

        return abs(angle2 - angle1)

    def _score_parallel_ways(self, current_way: Way, candidate_way: Way) -> float:
        if len(current_way.nodes) < 2 or len(candidate_way.nodes) < 2:
            return 0

        current_bearing = self._calculate_bearing(current_way.nodes[0], current_way.nodes[-1])
        candidate_bearing = self._calculate_bearing(candidate_way.nodes[0], candidate_way.nodes[-1])

        bearing_diff = abs(current_bearing - candidate_bearing)
        if bearing_diff > 20 and bearing_diff < 340:  # Not parallel
            return 0

        min_distance = np.min([self._point_to_line_distance(node.lat, node.lon,
                                                            candidate_way.nodes[0].lat, candidate_way.nodes[0].lon,
                                                            candidate_way.nodes[-1].lat, candidate_way.nodes[-1].lon)
                               for node in current_way.nodes])

        return 30 if 5 < min_distance < 20 else 0  # Boost score for potential lane change

    @staticmethod
    def _bbox_intersects(bbox1, bbox2):
        return not (bbox1[2] < bbox2[0] or bbox1[0] > bbox2[2] or
                    bbox1[3] < bbox2[1] or bbox1[1] > bbox2[3])