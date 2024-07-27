
from openpilot.dp_ext.selfdrive.tetood.lib.speed_camera_loader import SpeedCameraLoader
from typing import Dict
from openpilot.common.basedir import BASEDIR
import os
import csv


class TaiwanSpeedCameraLoader(SpeedCameraLoader):
    def __init__(self, data_source: str = None, data_type: str = 'osm_json'):
        self.data_source = os.path.join(BASEDIR, "dp_ext", "selfdrive", "tetood", "assets", "taiwan_speed_camera_2024_06_07.csv")
        self.data_type = "csv"
        self.speed_cameras = {}

    def _load_from_csv(self) -> Dict[int, Dict[str, any]]:
        if not self.speed_cameras:
            with open(self.data_source, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                next(reader)
                i = 0
                for row in reader:
                    camera_id = int(f"101{i}")
                    place = row['Address']
                    self.speed_cameras[camera_id] = {
                        'lat': float(row['Latitude']),
                        'lon': float(row['Longitude']),
                        'tags': {"place": place, "maxspeed": float(row['limit'])},
                    }
                    i += 1
        return self.speed_cameras