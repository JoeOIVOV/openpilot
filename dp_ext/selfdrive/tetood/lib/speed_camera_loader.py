import csv
import json
from typing import Dict

class SpeedCameraLoader:
    def __init__(self, data_source: str = None, data_type: str = 'osm_json'):
        self.data_source = data_source
        self.data_type = data_type

    def load_speed_cameras(self, prefetched_data: Dict = None) -> Dict[int, Dict[str, any]]:
        if self.data_type == 'csv':
            return self._load_from_csv()
        elif self.data_type == 'osm_json':
            return self._load_from_osm_json(prefetched_data)
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")

    def _load_from_csv(self) -> Dict[int, Dict[str, any]]:
        speed_cameras = {}
        with open(self.data_source, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                camera_id = int(row['id'])
                speed_cameras[camera_id] = {
                    'lat': float(row['latitude']),
                    'lon': float(row['longitude']),
                    'tags': json.loads(row.get('tags', '{}'))
                }
        return speed_cameras

    def _load_from_osm_json(self, prefetched_data: Dict) -> Dict[int, Dict[str, any]]:
        speed_cameras = {}
        for element in prefetched_data['elements']:
            if element['type'] == 'node' and element.get('tags', {}).get('highway') == 'speed_camera':
                camera_id = element['id']
                speed_cameras[camera_id] = {
                    'lat': float(element['lat']),
                    'lon': float(element['lon']),
                    'tags': element.get('tags', {})
                }
        return speed_cameras