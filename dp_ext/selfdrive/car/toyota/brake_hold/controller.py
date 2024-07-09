#!/usr/bin/env python3
# The MIT License
#
# Copyright (c) 2024-, Alexandre Sato, Rick Lan.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# code originally by:
# Alexandre Sato: https://github.com/AlexandreSato

# rewrite for easier integration hence the license declaration above.

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