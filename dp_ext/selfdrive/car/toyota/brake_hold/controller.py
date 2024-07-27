#!/usr/bin/env python3
# code originally by:
# Alexandre Sato: https://github.com/AlexandreSato

from openpilot.dp_ext.selfdrive.car.toyota.brake_hold.common import ENABLED
from openpilot.dp_ext.selfdrive.car.toyota.brake_hold.can import create_brakehold_command
from opendbc.can.packer import CANPacker

class BrakeHoldController:
    def __init__(self):
        self._enabled = ENABLED
        self.packer = CANPacker("toyota_brake_hold")
        pass

    def get_can_sends(self, frame, can_sends, brakehold_governor, stock_aeb):
        if not self._enabled:
            return can_sends

        # AleSato's Automatic Brake Hold
        if frame % 2 == 0:
            if brakehold_governor:
                can_sends.append(create_brakehold_command(self.packer, {}, True if frame % 730 < 727 else False))
            else:
                can_sends.append(create_brakehold_command(self.packer, stock_aeb, False))

        return can_sends