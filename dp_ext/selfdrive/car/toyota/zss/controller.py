#!/usr/bin/env python3
# Code was inspired from Erich Moraga (https://github.com/ErichMoraga/)

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
