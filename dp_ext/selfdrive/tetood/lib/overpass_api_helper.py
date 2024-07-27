
import requests
import numpy as np
from openpilot.dp_ext.selfdrive.tetood.lib.utils import R

class OverpassAPIHelper:
    def __init__(self):
        self.url = 'https://overpass-api.de/api/interpreter'
        # self.url = 'https://overpass.kumi.systems/api/interpreter'
        self.headers = {'Accept-Encoding': 'gzip'}

    def fetch_data(self, lat, lon, radius=3500, high_speed=True):
        """Fetch data from Overpass API based on the given GPS coordinates."""
        bbox_angle = np.degrees(radius / R)
        # fetch all ways and nodes on this ways in bbox
        bbox_str = f'{str(lat - bbox_angle)},{str(lon - bbox_angle)},{str(lat + bbox_angle)},{str(lon + bbox_angle)}'
        excl_way_types = 'pedestrian|footway|path|corridor|bridleway|steps|cycleway|construction|bus_guideway|escape|track'
        overpass_query = f"""
        [out:json][timeout:25][bbox:{bbox_str}];
        (
          way[highway][highway!~"^({excl_way_types})$"];
        ) -> .allways;
        (.allways;>;);
        out body;
        """
        print(overpass_query)
        try:
          response = requests.get(self.url, params={'data': overpass_query}, headers=self.headers)
        except:
          return None
        return response.json()
