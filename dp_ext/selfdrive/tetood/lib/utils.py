from typing import Tuple
import math

R = 6371000  # Earth's radius in meters

def haversine_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calculate_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate bearing of two points"""
    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])

    dlon = lon2 - lon1

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    initial_bearing = math.atan2(y, x)

    # Convert to degrees
    initial_bearing = math.degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360

    return bearing


def angle_diff(bearing1: float, bearing2 :float) -> float:
    # Calculate the absolute angle difference
    return abs((bearing1 - bearing2 + 180) % 360 - 180)

def feature_is_ahead(current_bearing: float, bearing_to_feature: float, within_deg: float = 15.):
    # Consider features within a 60-degree cone in front of the vehicle
    return angle_diff(current_bearing, bearing_to_feature) <= within_deg


def calculate_predicted_position(point: Tuple[float, float], bearing: float, distance: float) -> Tuple[float, float]:
    # Convert bearing to radians
    bearing_rad = math.radians(bearing)

    # Convert lat and lon from degrees to radians
    lat_rad = math.radians(point[0])
    lon_rad = math.radians(point[1])

    # Calculate the new latitude
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance / R) +
                            math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing_rad))

    # Calculate the new longitude
    new_lon_rad = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(distance / R) * math.cos(lat_rad),
                                       math.cos(distance / R) - math.sin(lat_rad) * math.sin(new_lat_rad))

    # Convert the new latitude and longitude from radians to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon

def point_to_line_distance(px, py, x1, y1, x2, y2):
    numerator = abs((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1)
    denominator = ((y2-y1)**2 + (x2-x1)**2)**0.5
    return numerator / denominator if denominator != 0 else float('inf')