import math
from typing import List, Dict, Tuple, Optional
from rtree import index
import numpy as np
from functools import lru_cache, cached_property

PADDING = 0.0001
LANE_WIDTH = 3.7  # meters
MIN_WAY_DIST = 500  # meters
TO_RADIANS = math.pi / 180.0

class Position:
    """
    Represents a geographic position with latitude, longitude, bearing, and speed.
    """
    def __init__(self, latitude: float, longitude: float, bearing: float, speed: float):
        self.latitude = latitude
        self.longitude = longitude
        self.bearing = bearing
        self.speed = speed

class Coordinates:
    """
    Represents a geographic coordinate with latitude and longitude.
    """
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

class Way:
    """
    Represents a road or path in the map.
    """
    def __init__(self, id: int, nodes: List[Coordinates], name: str, ref: str, oneway: bool, lanes: int, tags: Dict[str, str]):
        self.id = id
        self.nodes = nodes
        self.name = name
        self.ref = ref
        self.oneway = oneway
        self.lanes = max(lanes, 2)
        self.tags = tags

    def get_tag(self, key: str, default: str = None) -> str:
        """
        Get a tag value by its key.

        Args:
            key (str): The tag key to look up.
            default (str, optional): The default value to return if the key is not found.

        Returns:
            str: The value of the tag, or the default value if not found.
        """
        return self.tags.get(key, default)

    @cached_property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Calculate and cache the bounding box of the way.
        Returns a tuple of (min_lat, min_lon, max_lat, max_lon).
        """
        lats = [node.latitude for node in self.nodes]
        lons = [node.longitude for node in self.nodes]
        return (min(lats), min(lons), max(lats), max(lons))

class OnWayResult:
    """
    Represents the result of checking if a position is on a way.
    """
    def __init__(self, on_way: bool, distance: float, is_forward: bool):
        self.on_way = on_way
        self.distance = distance
        self.is_forward = is_forward

class CurrentWay:
    """
    Represents the current way a position is on, with additional information.
    """
    def __init__(self, way: Way, distance: float, on_way: OnWayResult, start_position: Coordinates, end_position: Coordinates):
        self.way = way
        self.distance = distance
        self.on_way = on_way
        self.start_position = start_position
        self.end_position = end_position

class NextWayResult:
    """
    Represents a potential next way in the route.
    """
    def __init__(self, way: Way, is_forward: bool, start_position: Coordinates, end_position: Coordinates):
        self.way = way
        self.is_forward = is_forward
        self.start_position = start_position
        self.end_position = end_position

class AdvancedMapMatcher:
    """
    A class that performs advanced map matching using various algorithms and techniques.
    """
    def __init__(self, road_data: Dict):
        self.ways = self._load_ways(road_data)
        self.rtree = index.Index()
        self.gps_buffer: List[Position] = []
        self.current_way: Optional[CurrentWay] = None
        self._build_rtree()
        self.way_vectors = {}
        self._precompute_way_vectors()

        # Hidden Markov Model (HMM) variables
        self.hmm_states: List[Tuple[int, int]] = []
        self.hmm_transitions: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        self.current_timestep = 0
        self.current_viterbi_path: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        self.current_viterbi_prob: Dict[Tuple[int, int], float] = {}

        self.initialize_hmm()

    def _load_ways(self, road_data: Dict) -> List[Way]:
        """
        Load ways from the provided road data.

        Args:
            road_data (Dict): Dictionary containing road network data.

        Returns:
            List[Way]: List of Way objects created from the road data.
        """
        ways = []
        nodes_dict = {}  # To store node id to coordinates mapping

        # First, create a dictionary of node id to coordinates
        for element in road_data['elements']:
            if element['type'] == 'node':
                nodes_dict[element['id']] = Coordinates(element['lat'], element['lon'])

        # Then, create Way objects
        for element in road_data['elements']:
            if element['type'] == 'way':
                try:
                    nodes = [nodes_dict[node_id] for node_id in element['nodes'] if node_id in nodes_dict]
                    if len(nodes) < 2:
                        print(f"Warning: Way {element['id']} has less than 2 valid nodes. Skipping.")
                        continue

                    tags = element.get('tags', {})
                    way = Way(
                        id=element['id'],
                        nodes=nodes,
                        name=tags.get('name', ''),
                        ref=tags.get('ref', ''),
                        oneway=tags.get('oneway', 'no').lower() == 'yes',
                        lanes=int(tags.get('lanes', '2')),
                        tags=tags  # Store all tags
                    )
                    ways.append(way)
                except KeyError as e:
                    print(f"Error processing way {element['id']}: {e}")
                except ValueError as e:
                    print(f"Error processing way {element['id']}: {e}")

        return ways

    def _build_rtree(self):
        """
        Build an R-tree spatial index for efficient spatial queries.
        """
        for idx, way in enumerate(self.ways):
            # Access bounding_box as a property, not a method
            self.rtree.insert(idx, way.bounding_box, obj=way)

    def initialize_hmm(self):
        """
        Initialize the Hidden Markov Model for map matching.
        """
        self.build_hmm()
        self.current_timestep = 0
        self.current_viterbi_path = {}
        self.current_viterbi_prob = {}

        initial_prob = 1.0 / len(self.hmm_states)
        for state in self.hmm_states:
            self.current_viterbi_path[state] = [state]
            self.current_viterbi_prob[state] = initial_prob

    def build_hmm(self):
        """
        Build the Hidden Markov Model states and transitions.
        """
        # Create states for each segment of each way
        self.hmm_states = [(way.id, i) for way in self.ways for i in range(len(way.nodes) - 1)]

        # Create transitions between consecutive segments of the same way
        self.hmm_transitions = {
            (way.id, i): [(way.id, i + 1)] for way in self.ways for i in range(len(way.nodes) - 2)
        }

        # Add empty transitions for the last segment of each way
        for way in self.ways:
            self.hmm_transitions[(way.id, len(way.nodes) - 2)] = []

    @lru_cache(maxsize=1000)
    def on_way(self, way: Way, pos: Position) -> OnWayResult:
        """
        Determine if a position is on a given way.

        Args:
            way (Way): The way to check.
            pos (Position): The position to check.

        Returns:
            OnWayResult: An object containing whether the position is on the way,
                         the distance to the way, and if it's in the forward direction.
        """
        if self._is_within_bounding_box(way, pos):
            distance = self.distance_to_way(pos, way)
            lanes = max(way.lanes, 2)
            road_width_estimate = float(lanes) * LANE_WIDTH
            max_dist = 5 + road_width_estimate

            if distance < max_dist:
                is_forward = self.is_forward(way.nodes[0], way.nodes[-1], pos.bearing)
                if not is_forward and way.oneway:
                    return OnWayResult(False, distance, is_forward)
                return OnWayResult(True, distance, is_forward)

        return OnWayResult(False, float('inf'), False)

    def _find_nearest_ways(self, pos: Position, k: int = 5) -> List[Way]:
        """
        Find the k nearest ways to a given position using the R-tree spatial index.

        Args:
            pos (Position): The position to search from.
            k (int): The number of nearest ways to return.

        Returns:
            List[Way]: A list of the k nearest ways.
        """
        nearest = list(self.rtree.nearest((pos.latitude, pos.longitude, pos.latitude, pos.longitude), k))
        return [self.ways[i] for i in nearest]

    def _distance_to_end_of_way(self, pos: Position, way: Way, is_forward: bool) -> float:
        """
        Calculate the distance from the current position to the end of the way.

        Args:
            pos (Position): The current position.
            way (Way): The way to calculate the distance for.
            is_forward (bool): Whether we're moving forward on the way.

        Returns:
            float: The distance to the end of the way in meters.
        """
        end_node = way.nodes[-1] if is_forward else way.nodes[0]
        return self.haversine_distance(
            Coordinates(pos.latitude, pos.longitude),
            end_node
        )

    def next_ways(self, pos: Position, current_way: CurrentWay, is_forward: bool) -> List[NextWayResult]:
        """
        Find the next ways from the current position and way.

        Args:
            pos (Position): The current position.
            current_way (CurrentWay): The current way.
            is_forward (bool): Whether to look for ways in the forward direction.

        Returns:
            List[NextWayResult]: A list of potential next ways.
        """
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

            # Use _find_nearest_ways instead of checking all ways
            nearest_ways = self._find_nearest_ways(start_pos, k=5)
            nw = self._find_best_next_way(way, nearest_ways, forward)

            if nw is None:
                break

            next_ways.append(nw)
            way = nw.way
            start_pos = Position(nw.start_position.latitude, nw.start_position.longitude, 0, 0)
            forward = nw.is_forward

        if not next_ways:
            nearest_ways = self._find_nearest_ways(pos, k=5)
            nw = self._find_best_next_way(current_way.way, nearest_ways, is_forward)
            if nw:
                next_ways.append(nw)

        return next_ways

    def _find_best_next_way(self, current_way: Way, candidate_ways: List[Way], is_forward: bool) -> Optional[NextWayResult]:
        """
        Find the best next way from a list of candidate ways.

        Args:
            current_way (Way): The current way.
            candidate_ways (List[Way]): List of candidate ways to choose from.
            is_forward (bool): Whether to look for the next way in the forward direction.

        Returns:
            Optional[NextWayResult]: The best next way result, or None if no suitable way is found.
        """
        match_node = current_way.nodes[-1] if is_forward else current_way.nodes[0]
        match_bearing_node = current_way.nodes[-2] if is_forward else current_way.nodes[1]

        # Filter candidate ways to those that connect to the current way
        connecting_ways = [way for way in candidate_ways if match_node in (way.nodes[0], way.nodes[-1])]

        if not connecting_ways:
            return None

        # First, check for ways with matching names
        name_matches = [way for way in connecting_ways if way.name == current_way.name]
        if name_matches:
            return self._select_best_way(name_matches, match_node, match_bearing_node)

        # Then, check for ways with matching references
        ref_matches = [way for way in connecting_ways if way.ref == current_way.ref]
        if ref_matches:
            return self._select_best_way(ref_matches, match_node, match_bearing_node)

        # Finally, select the way with the least curvature
        return self._select_best_way(connecting_ways, match_node, match_bearing_node)


    def _get_way_start_end(self, way: Way, is_forward: bool) -> Tuple[Coordinates, Coordinates]:
        """
        Get the start and end coordinates of a way based on the direction of travel.

        Args:
            way (Way): The way to get start and end coordinates for.
            is_forward (bool): Whether the way is being traversed in the forward direction.

        Returns:
            Tuple[Coordinates, Coordinates]: The start and end coordinates of the way.
        """
        if is_forward:
            return way.nodes[0], way.nodes[-1]
        else:
            return way.nodes[-1], way.nodes[0]


    def _calculate_angle(self, p1: Coordinates, p2: Coordinates, p3: Coordinates) -> float:
        """
        Calculate the angle between three points.

        Args:
            p1 (Coordinates): First point
            p2 (Coordinates): Second point (vertex of the angle)
            p3 (Coordinates): Third point

        Returns:
            float: Angle in radians
        """
        v1 = (p1.latitude - p2.latitude, p1.longitude - p2.longitude)
        v2 = (p3.latitude - p2.latitude, p3.longitude - p2.longitude)

        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag_v2 = math.sqrt(v2[0]**2 + v2[1]**2)

        cos_angle = dot_product / (mag_v1 * mag_v2)

        # Clamp the value to avoid domain errors due to floating point precision
        cos_angle = max(-1.0, min(1.0, cos_angle))

        return math.acos(cos_angle)

    def _select_best_way(self, ways: List[Way], match_node: Coordinates, match_bearing_node: Coordinates) -> NextWayResult:
        """
        Select the best way from a list of ways based on curvature and direction.

        Args:
            ways (List[Way]): List of candidate ways.
            match_node (Coordinates): The node where the ways should connect.
            match_bearing_node (Coordinates): The node used to calculate the bearing of the current way.

        Returns:
            NextWayResult: The best next way result.
        """
        best_way = None
        best_curvature = float('inf')
        best_is_forward = False

        for way in ways:
            is_forward = way.nodes[0] == match_node
            if not is_forward and way.oneway:
                continue

            bearing_node = way.nodes[1] if is_forward else way.nodes[-2]
            curvature = abs(self._calculate_angle(match_bearing_node, match_node, bearing_node))

            if curvature < best_curvature:
                best_way = way
                best_curvature = curvature
                best_is_forward = is_forward

        if best_way is None:
            return None

        start, end = self._get_way_start_end(best_way, best_is_forward)
        return NextWayResult(best_way, best_is_forward, start, end)

    def update_gps(self, pos: Position) -> Optional[CurrentWay]:
        """
        Update the map matcher with a new GPS position.

        Args:
            pos (Position): The new GPS position.

        Returns:
            Optional[CurrentWay]: The current way if found, or None if not on any way.
        """
        self.gps_buffer.append(pos)
        if len(self.gps_buffer) > 25:
            self.gps_buffer.pop(0)

        # Check if we're still on the current way
        if self.current_way and self.on_way(self.current_way.way, pos).on_way:
            # Simple update if still on the same way
            return self._update_current_way(pos)

        # If not, find the nearest ways and check them
        nearest_ways = self._find_nearest_ways(pos)
        for way in nearest_ways:
            on_way_result = self.on_way(way, pos)
            if on_way_result.on_way:
                return self._update_current_way(pos, way, on_way_result)

        # Only use HMM if we can't find a clear match
        if self.current_timestep % 5 == 0:
            self._viterbi_step(pos)

        self.current_timestep += 1

        if not self.current_viterbi_prob:
            return None

        most_likely_state = max(self.current_viterbi_prob, key=self.current_viterbi_prob.get)
        way = next((way for way in self.ways if way.id == most_likely_state[0]), None)

        if way is None:
            return None

        on_way_result = self.on_way(way, pos)
        start, end = self._get_way_start_end(way, on_way_result.is_forward)

        current_way = CurrentWay(way, on_way_result.distance, on_way_result, start, end)

        # Use next_ways to get upcoming ways
        upcoming_ways = self.next_ways(pos, current_way, on_way_result.is_forward)

        # You could store these upcoming ways for future use or return them along with the current way
        self.upcoming_ways = upcoming_ways

        return current_way

    def _update_current_way(self, pos: Position, way: Way = None, on_way_result: OnWayResult = None) -> CurrentWay:
        """
        Update the current way based on the new position.

        Args:
            pos (Position): The new GPS position.
            way (Way, optional): The way to update to. If None, uses the current way.
            on_way_result (OnWayResult, optional): The result of checking if the position is on the way.

        Returns:
            CurrentWay: The updated current way.
        """
        if way is None:
            way = self.current_way.way
        if on_way_result is None:
            on_way_result = self.on_way(way, pos)

        start, end = self._get_way_start_end(way, on_way_result.is_forward)
        current_way = CurrentWay(way, on_way_result.distance, on_way_result, start, end)

        # Update upcoming ways
        self.upcoming_ways = self.next_ways(pos, current_way, on_way_result.is_forward)

        return current_way

    def _viterbi_step(self, pos: Position):
        """
        Perform a step of the Viterbi algorithm for Hidden Markov Model-based map matching.

        This method updates the probabilities of being in each state (way segment) given the new position.

        Args:
            pos (Position): The new GPS position.
        """
        new_viterbi_prob = {}
        new_viterbi_path = {}

        for state in self.hmm_states:
            way = next((w for w in self.ways if w.id == state[0]), None)
            if way is None:
                continue

            emission_prob = self._emission_probability(pos, way, state[1])
            max_prob = float('-inf')
            max_prev_state = None

            for prev_state in self.hmm_transitions.get(state, []):
                if prev_state in self.current_viterbi_prob:
                    transition_prob = self._transition_probability(prev_state, state)

                    # Consider upcoming ways in transition probability
                    if hasattr(self, 'upcoming_ways'):
                        upcoming_way_ids = [w.way.id for w in self.upcoming_ways]
                        if state[0] in upcoming_way_ids:
                            transition_prob *= 1.2  # Increase probability for upcoming ways

                    prob = self.current_viterbi_prob[prev_state] + math.log(transition_prob) + math.log(emission_prob)
                    if prob > max_prob:
                        max_prob = prob
                        max_prev_state = prev_state

            if max_prev_state is not None:
                new_viterbi_prob[state] = max_prob
                new_viterbi_path[state] = self.current_viterbi_path[max_prev_state] + [state]

        self.current_viterbi_prob = new_viterbi_prob
        self.current_viterbi_path = new_viterbi_path

    @lru_cache(maxsize=1000)
    def _emission_probability(self, pos: Position, way: Way, segment_index: int) -> float:
        """
        Calculate the emission probability for a given position and way segment.

        This probability represents how likely it is that the GPS position would be observed
        if the true position was on the given way segment.

        Args:
            pos (Position): The current GPS position.
            way (Way): The candidate way.
            segment_index (int): The index of the segment in the way.

        Returns:
            float: The emission probability.
        """
        start_node = way.nodes[segment_index]
        end_node = way.nodes[segment_index + 1]
        distance = self.point_to_line_distance(pos.latitude, pos.longitude,
                                               start_node.latitude, start_node.longitude,
                                               end_node.latitude, end_node.longitude)
        return math.exp(-distance / 20.0)  # Assuming GPS error std dev of 20 meters

    @lru_cache(maxsize=1000)
    def _transition_probability(self, prev_state: Tuple[int, int], curr_state: Tuple[int, int]) -> float:
        """
        Calculate the transition probability between two states.

        Args:
            prev_state (Tuple[int, int]): The previous state (way_id, segment_index).
            curr_state (Tuple[int, int]): The current state (way_id, segment_index).

        Returns:
            float: The transition probability.
        """
        prev_way = next((way for way in self.ways if way.id == prev_state[0]), None)
        curr_way = next((way for way in self.ways if way.id == curr_state[0]), None)

        if prev_way is None or curr_way is None:
            return 0.0  # Invalid transition

        if prev_state[0] == curr_state[0]:  # Same way
            if curr_state[1] == prev_state[1] + 1:  # Next segment
                return 0.95
            else:
                # Handle the case where the way has 3 or fewer nodes
                segment_count = len(prev_way.nodes) - 1
                if segment_count <= 2:
                    return 0.05 if curr_state[1] != prev_state[1] else 0.0
                else:
                    return 0.05 / (segment_count - 1)  # Uniform distribution over other segments
        else:  # Different way
            return 0.05 / (len(self.ways) - 1)  # Uniform distribution over other ways

    @staticmethod
    def _is_within_bounding_box(way: Way, pos: Position) -> bool:
        """
        Check if a position is within the bounding box of a way.

        Args:
            way (Way): The way to check.
            pos (Position): The position to check.

        Returns:
            bool: True if the position is within the bounding box, False otherwise.
        """
        bbox = way.bounding_box
        return (bbox[0] - PADDING <= pos.latitude <= bbox[2] + PADDING and
                bbox[1] - PADDING <= pos.longitude <= bbox[3] + PADDING)

    def _precompute_way_vectors(self):
        """
        Precompute vectors for each way to speed up distance calculations.
        """
        self.way_vectors = {}
        for way in self.ways:
            coords = np.array([(node.latitude, node.longitude) for node in way.nodes])
            self.way_vectors[way.id] = coords

    def distance_to_way(self, pos: Position, way: Way) -> float:
        """
        Calculate the minimum distance from a position to a way.

        Args:
            pos (Position): The position to check.
            way (Way): The way to calculate distance to.

        Returns:
            float: The minimum distance from the position to the way.
        """
        way_vector = self.way_vectors[way.id]
        pos_vector = np.array([pos.latitude, pos.longitude])
        distances = np.sum((way_vector[:-1] - pos_vector)**2, axis=1)
        return np.min(distances)**0.5

    @staticmethod
    def is_forward(start: Coordinates, end: Coordinates, bearing: float) -> bool:
        """
        Determine if the bearing is in the forward direction of the way.

        Args:
            start (Coordinates): The start coordinates of the way.
            end (Coordinates): The end coordinates of the way.
            bearing (float): The bearing to check.

        Returns:
            bool: True if the bearing is in the forward direction, False otherwise.
        """
        way_bearing = AdvancedMapMatcher.calculate_bearing(start, end)
        return abs((way_bearing - bearing + 180) % 360 - 180) < 90

    @staticmethod
    def calculate_bearing(start: Coordinates, end: Coordinates) -> float:
        """
        Calculate the bearing between two coordinates.

        Args:
            start (Coordinates): The start coordinates.
            end (Coordinates): The end coordinates.

        Returns:
            float: The bearing in degrees.
        """
        y = math.sin(end.longitude - start.longitude) * math.cos(end.latitude)
        x = math.cos(start.latitude) * math.sin(end.latitude) - math.sin(start.latitude) * math.cos(end.latitude) * math.cos(end.longitude - start.longitude)
        return (math.atan2(y, x) * 180 / math.pi + 360) % 360

    @staticmethod
    def haversine_distance(start: Coordinates, end: Coordinates) -> float:
        """
        Calculate the Haversine distance between two coordinates.

        Args:
            start (Coordinates): The start coordinates.
            end (Coordinates): The end coordinates.

        Returns:
            float: The distance in meters.
        """
        R = 6371000  # Earth radius in meters
        lat1, lon1 = start.latitude * TO_RADIANS, start.longitude * TO_RADIANS
        lat2, lon2 = end.latitude * TO_RADIANS, end.longitude * TO_RADIANS
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    @staticmethod
    def point_to_line_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """
        Calculate the perpendicular distance from a point to a line segment.

        Args:
            px (float): X-coordinate of the point.
            py (float): Y-coordinate of the point.
            x1 (float): X-coordinate of the first point of the line segment.
            y1 (float): Y-coordinate of the first point of the line segment.
            x2 (float): X-coordinate of the second point of the line segment.
            y2 (float): Y-coordinate of the second point of the line segment.

        Returns:
            float: The perpendicular distance from the point to the line segment.
        """
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:  # The segment is actually a point
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        t = ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)
        if t < 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        elif t > 1:
            return math.sqrt((px - x2)**2 + (py - y2)**2)
        else:
            return abs((dy*px - dx*py + x2*y1 - y2*x1) / math.sqrt(dx**2 + dy**2))