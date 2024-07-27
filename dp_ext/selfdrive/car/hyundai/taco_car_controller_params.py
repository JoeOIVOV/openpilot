#!/usr/bin/env python3
from openpilot.selfdrive.car.hyundai.values import CarControllerParams

class TacoCarControllerParams(CarControllerParams):

    # rick - re-implement taco mode, thanks to @stupefacient
    def update(self, v_ego_raw: float = 100.):
        if v_ego_raw < 11:
            self.STEER_MAX = 384
            self.STEER_DRIVER_ALLOWANCE = 350
            self.STEER_DRIVER_MULTIPLIER = 2
            self.STEER_THRESHOLD = 350
            self.STEER_DELTA_UP = 10
            self.STEER_DELTA_DOWN = 10
        else:
            # stock values
            self.STEER_MAX = 270
            self.STEER_DRIVER_ALLOWANCE = 250
            self.STEER_DRIVER_MULTIPLIER = 2
            self.STEER_THRESHOLD = 250
            self.STEER_DELTA_UP = 2
            self.STEER_DELTA_DOWN = 3

