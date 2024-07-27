#!/usr/bin/env python3
from openpilot.common.numpy_fast import interp

DP_ACCEL_STOCK = 0
DP_ACCEL_ECO = 1
DP_ACCEL_NORMAL = 2
DP_ACCEL_SPORT = 3

# accel profile by @arne182 modified by cgw
_DP_CRUISE_MIN_V =       [-1.10,  -1.20,  -1.10,  -1.10,  -1.02,  -1.02,  -1.02]
_DP_CRUISE_MIN_V_ECO =   [-1.00,  -1.10,  -1.00,  -1.00,  -1.00,  -1.00,  -1.00]
_DP_CRUISE_MIN_V_SPORT = [-1.20,  -1.30,  -1.20,  -1.20,  -1.05, - 1.05, -1.05]
_DP_CRUISE_MIN_BP =      [0.,     0.3,    0.6,    8.33,   16.,   30.,   40.]

_DP_CRUISE_MAX_V =       [2.8, 2.8, 2.4, 1.90, 1.05,  .81, .625,  .42,  .348, .12]
_DP_CRUISE_MAX_V_ECO =   [2.4, 2.4, 2.1, 1.60, .965, .785, .576,  .377, .323, .083]
_DP_CRUISE_MAX_V_SPORT = [3.5, 3.5, 2.8, 2.4, 1.4,  .85,  .795,  .65,  .40,  .2]
_DP_CRUISE_MAX_BP =      [0.,  1.,  6.,  8.,  11.,  15.,  20.,   25.,  30.,  55.]

class AccelController:

  def __init__(self):
    # self._params = Params()
    self._profile = DP_ACCEL_STOCK

  def set_profile(self, profile):
    try:
      self._profile = int(profile) if int(profile) in [DP_ACCEL_STOCK, DP_ACCEL_ECO, DP_ACCEL_NORMAL, DP_ACCEL_SPORT] else DP_ACCEL_STOCK
    except:
      self._profile = DP_ACCEL_STOCK

  def _dp_calc_cruise_accel_limits(self, v_ego):
    if self._profile == DP_ACCEL_ECO:
      min_v = _DP_CRUISE_MIN_V_ECO
      max_v = _DP_CRUISE_MAX_V_ECO
    elif self._profile == DP_ACCEL_SPORT:
      min_v = _DP_CRUISE_MIN_V_SPORT
      max_v = _DP_CRUISE_MAX_V_SPORT
    else:
      min_v = _DP_CRUISE_MIN_V
      max_v = _DP_CRUISE_MAX_V

    a_cruise_min = interp(v_ego, _DP_CRUISE_MIN_BP, min_v)
    a_cruise_max = interp(v_ego, _DP_CRUISE_MAX_BP, max_v)
    return a_cruise_min, a_cruise_max

  def get_accel_limits(self, v_ego, accel_limits):
    return accel_limits if self._profile == DP_ACCEL_STOCK else self._dp_calc_cruise_accel_limits(v_ego)

  def is_enabled(self):
    return self._profile != DP_ACCEL_STOCK
