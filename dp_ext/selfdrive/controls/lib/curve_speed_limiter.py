#!/usr/bin/env python3

from openpilot.common.params import Params
import numpy as np
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.common.numpy_fast import interp



class CurveSpeedLimiter:
    def __init__(self):
        self._enabled = Params().get_bool("dp_long_curve_speed_limiter")
        self._v = 0.
        pass

    def update(self, v_ego, z, v):
        if not self._enabled:
            return
        max_lat_accel = interp(v_ego, [5, 10, 20], [1.5, 2.0, 3.0])
        curvatures = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, z) / np.clip(v, 0.3, 100.0)
        max_v = np.sqrt(max_lat_accel / (np.abs(curvatures) + 1e-3)) - 2.0
        self._v = np.minimum(max_v, v)

    def get_v(self, v):
        return self._v if self._enabled else v