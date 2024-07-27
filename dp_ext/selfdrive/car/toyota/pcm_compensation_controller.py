#!/usr/bin/env python3
# code originally from @cydia2020, see https://github.com/commaai/openpilot/pull/30697/files

from openpilot.common.numpy_fast import clip, interp

# PCM compensatory force calculation threshold
# a variation in accel command is more pronounced at higher speeds, let compensatory forces ramp to zero before
# applying when speed is high
COMPENSATORY_CALCULATION_THRESHOLD_V = [-0.3, -0.25, 0.]  # m/s^2
COMPENSATORY_CALCULATION_THRESHOLD_BP = [0., 11., 23.]  # m/s

class PCMCompensationController:
    def __init__(self, cp, params, is_enabled):
        self.cp = cp
        self.params = params
        self.prohibit_neg_calculation = True
        self._is_enabled = is_enabled
        pass

    def get_pcm_accel_cmd(self, long_active, v_ego, pcm_neutral_force, accel):
        # prohibit negative compensatory calculations when first activating long after accelerator depression or engagement
        if not long_active:
            self.prohibit_neg_calculation = True
        comp_thresh = interp(v_ego, COMPENSATORY_CALCULATION_THRESHOLD_BP, COMPENSATORY_CALCULATION_THRESHOLD_V)
        # don't reset until a reasonable compensatory value is reached
        if pcm_neutral_force > comp_thresh * self.cp.mass:
            self.prohibit_neg_calculation = False
        # limit minimum to only positive until first positive is reached after engagement, don't calculate when long isn't active
        if long_active and not self.prohibit_neg_calculation:
            accel_offset = pcm_neutral_force / self.cp.mass
        else:
            accel_offset = 0.
        # only calculate pcm_accel_cmd when long is active to prevent disengagement from accelerator depression
        if long_active:
            pcm_accel_cmd = clip(accel + accel_offset, self.params.ACCEL_MIN, self.params.ACCEL_MAX)
        else:
            pcm_accel_cmd = 0.

        return pcm_accel_cmd

    def is_enabled(self):
        return self._is_enabled
