#!/usr/bin/env python3

import numpy as np
from openpilot.common.params import Params

class RoadEdgeDetector:

  def __init__(self):
    self._is_enabled = Params().get_bool("dp_lat_road_edge_detection")

  def get_road_edge_detected(self, blindspot_detected, road_edge_stds, lane_line_probs, left_blinker, right_blinker):
    if blindspot_detected:
      return True

    if not self._is_enabled:
      return blindspot_detected

    # Calculate probabiities for detecting road edges and lane lines
    left_road_edge_prob = np.clip(1.0 - road_edge_stds[0], 0.0, 1.0)
    left_lane_nearside_prob = lane_line_probs[0]

    right_road_edge_prob = np.clip(1.0 - road_edge_stds[1], 0.0, 1.0)
    right_lane_nearside_prob = lane_line_probs[3]

    # Check conditions for detecting road edges
    if right_blinker and right_road_edge_prob > 0.35 and right_lane_nearside_prob < 0.2 and left_lane_nearside_prob >= right_lane_nearside_prob:
      return True
    elif left_blinker and left_road_edge_prob > 0.35 and left_lane_nearside_prob < 0.2 and right_lane_nearside_prob >= left_lane_nearside_prob:
      return True

    return blindspot_detected
