#!/usr/bin/env python3

from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params

class AlternativeDrivingPersonalityController:
    def __init__(self):
        params = Params()
        # try except to avoid issue in longitudinal testing
        try:
            self._speed = int(params.get("dp_long_alt_driving_personality_speed")) * CV.KPH_TO_MS
        except:
            self._speed = 0

        self._mode = params.get_bool("dp_long_alt_driving_personality_mode")
        self._active = False

    def update(self, v_ego):
        self._active = self._speed > 0 and v_ego < self._speed

    def get_personality(self, personality):
        return self._mode if self._active else personality

    def is_active(self):
        return self._active