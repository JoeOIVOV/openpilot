import math
import json
from typing import List, Tuple, Dict, Optional
from rtree import index

class Node:
    def __init__(self, id: int, lat: float, lon: float, tags: Dict = None):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.tags = tags or {}

class Way:
    def __init__(self, id: int, nodes: List[Node]):
        self.id = id
        self.nodes = nodes


class MapMatcher:
    def __init__(self, prefetched_data: Dict):
        # self.road_network = road_network
        # self.spatial_index = self._build_spatial_index()
        nodes, ways = self.parse_overpass_data(prefetched_data)
        self.nodes = {node.id: node for node in nodes}
        self.ways = ways
        self.way_dict = {way.id: way for way in ways}
        self.rtree = self._build_rtree()

    def _build_rtree(self):
        p = index.Property()
        p.dimension = 2
        rtree = index.Index(properties=p)
        for i, way in enumerate(self.ways):
            for node in way.nodes:
                rtree.insert(i, (node.lon, node.lat, node.lon, node.lat), obj=(way.id, node.id))
        return rtree

    def _distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def _find_closest_way_and_node(self, lat: float, lon: float) -> Tuple[int, int, float]:
        nearest = list(self.rtree.nearest((lon, lat, lon, lat), 1, objects=True))[0]
        way_id, node_id = nearest.object
        node = self.nodes[node_id]
        distance = self._distance(lat, lon, node.lat, node.lon)
        print(f"{way_id}, {node_id}, {distance}")
        return way_id, node_id, distance

    def _get_nearby_ways(self, lat: float, lon: float, radius: float) -> List[int]:
        # Convert radius from km to degrees (approximate)
        radius_deg = radius / 111.32  # 1 degree is approximately 111.32 km
        bbox = (lon - radius_deg, lat - radius_deg, lon + radius_deg, lat + radius_deg)
        return list(set(item.object[0] for item in self.rtree.intersection(bbox, objects=True)))

    def match(self, lat: float, lon: float, current_way: Optional[List[float]] = None, max_drift: float = 0.1) -> Tuple[int, int]:
        nearby_ways = self._get_nearby_ways(lat, lon, max_drift * 2)

        if current_way is None or current_way not in nearby_ways:
            return self._find_closest_way_and_node(lat, lon)
        else:
            min_distance = float('inf')
            best_way = current_way
            best_node = None

            for way_id in nearby_ways:
                way = self.way_dict[way_id]
                for node in way.nodes:
                    distance = self._distance(lat, lon, node.lat, node.lon)
                    if distance < min_distance:
                        min_distance = distance
                        best_way = way_id
                        best_node = node.id

            return best_way, best_node, min_distance

    def parse_overpass_data(self, data: str) -> Tuple[List[Node], List[Way]]:
        # json_data = json.loads(data)
        nodes = []
        ways = []
        node_dict = {}

        for element in data['elements']:
            if element['type'] == 'node':
                node = Node(element['id'], element['lat'], element['lon'], element.get('tags'))
                nodes.append(node)
                node_dict[node.id] = node
            elif element['type'] == 'way':
                way_nodes = [node_dict[node_id] for node_id in element['nodes'] if node_id in node_dict]
                way = Way(element['id'], way_nodes)
                ways.append(way)

        return nodes, ways
#
# # Example usage
# if __name__ == "__main__":
#     overpass_data = '''
#     [
#         {
#             "type": "node",
#             "id": 775379692,
#             "lat": 25.0804406,
#             "lon": 121.6071380
#         },
#         {
#             "type": "node",
#             "id": 775379741,
#             "lat": 25.0680739,
#             "lon": 121.6170474
#         },
#         {
#             "type": "node",
#             "id": 775379747,
#             "lat": 25.0733561,
#             "lon": 121.6058384,
#             "tags": {
#                 "addr:city": "台北市",
#                 "addr:country": "TW",
#                 "addr:district": "內湖區",
#                 "addr:housenumber": "16",
#                 "addr:postcode": "11486",
#                 "addr:street": "康寧路三段",
#                 "highway": "traffic_signals"
#             }
#         },
#         {
#             "type": "node",
#             "id": 775379748,
#             "lat": 25.0731973,
#             "lon": 121.6061928,
#             "tags": {
#                 "highway": "traffic_signals"
#             }
#         }
#     ]
#     '''
#
#     nodes, ways = parse_overpass_data(overpass_data)
#
#     # For this example, we'll create a dummy way using all the nodes
#     dummy_way = Way(1, nodes)
#     ways.append(dummy_way)
#
#     map_matcher = MapMatcher(nodes, ways)
#
#     # Test the map matching
#     current_way = None
#     current_node = None
#     test_positions = [
#         (25.0804406, 121.6071380),
#         (25.0733561, 121.6058384),
#         (25.0731973, 121.6061928),
#         (25.0680739, 121.6170474)
#     ]
#
#     for lat, lon in test_positions:
#         matched_way, matched_node = map_matcher.match(lat, lon, current_way)
#         print(f"Current position: {lat}, {lon}")
#         print(f"Matched way: {matched_way}, Matched node: {matched_node}")
#         current_way = matched_way
#         current_node = matched_node
#         print("---")