#!/usr/bin/env python3
# The MIT License
#
# Copyright (c) 2019-, Rick Lan, dragonpilot community, and a number of other of contributors.
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

# Code was inspired from Erich Moraga (https://github.com/ErichMoraga/)
# Rewrite due to poor written originally hence the license declaration above.

from openpilot.dp_ext.selfdrive.car.toyota.zss.common import ENABLED, ALKA
from opendbc.can.parser import CANParser
from cereal import messaging

THRESHOLD = 4.0
THRESHOLD_COUNT = 10

class ZSSController:
    def __init__(self):
        self._enabled = ENABLED
        self._dp_toyota_zss_active = False
        self._offset_compute_required = False
        self._lka_active_prev = False
        self._angle_offset = 0.
        self._threshold_count = 0

        # do not init pass here
        if not self._enabled:
            return

        self._dp_alka = ALKA
        self.can_sock = messaging.sub_sock('can')
        messages = [("SECONDARY_STEER_ANGLE", 0)]
        self.can_parser = CANParser('toyota_zss', messages, 0)


    def get_steering_angle_deg(self, main_on, cruise_active, steering_angle_deg):
        # off, fall back to stock
        if not self._enabled:
            return steering_angle_deg

        # too many failure, fallback to stock
        if self._threshold_count > THRESHOLD_COUNT:
            print("ZSS: Too many failure, fallback to stock.")
            return steering_angle_deg

        zorro_steer = self._get_zss_steer()

        self._compute_offset(main_on, cruise_active, steering_angle_deg, zorro_steer)

        new_steering_angle_deg = zorro_steer - self._angle_offset

        # error check, when difference between stock vs new angle deg is too large
        if abs(steering_angle_deg - new_steering_angle_deg) > THRESHOLD:
            self._threshold_count += 1

        # send back zss angle deg
        return new_steering_angle_deg

    def _get_zss_steer(self):
        can_strings = messaging.drain_sock_raw(self.can_sock, wait_for_one=True)
        self.can_parser.update_strings(can_strings)

        # reading data from sensor
        return self.can_parser.vl["SECONDARY_STEER_ANGLE"]["ZORRO_STEER"]

    def _compute_offset(self, main_on, cruise_active, steering_angle_deg, zorro_steer):
        # When alka is on, we check main_on state
        # cp_vl["PCM_CRUISE_2"]["MAIN_ON"] / cp_vl["PCM_CRUISE"]["CRUISE_ACTIVE"])
        lka_active = (self._dp_alka and main_on != 0) or bool(cruise_active)

        # only compute zss offset when lka is active
        if lka_active and not self._lka_active_prev:
            self._threshold_count = 0
            self._offset_compute_required = True # cruise was just activated, so allow offset to be recomputed
        self._lka_active_prev = lka_active

        # compute zss offset once
        if self._offset_compute_required:
            if abs(steering_angle_deg) > 1e-3 and abs(zorro_steer) > 1e-3:
                self._offset_compute_required = False
                self._angle_offset = zorro_steer - steering_angle_deg
