#!/usr/bin/env python3
# code originally by:
# arne182: https://github.com/arne182
# kumar:   https://github.com/rav4kumar

from openpilot.dp_ext.selfdrive.car.toyota.bsm.common import ENABLED
from opendbc.can.parser import CANParser
from cereal import messaging

class BSMState:
    def __init__(self):
        # bsm
        self._left_bsm = False
        self._left_bsm_distance_1 = 0
        self._left_bsm_distance_2 = 0
        self._left_bsm_counter = 0

        self._right_bsm = False
        self._right_bsm_distance_1 = 0
        self._right_bsm_distance_2 = 0
        self._right_bsm_counter = 0

        self._frame = 0

        self._enabled = ENABLED
        if self._enabled:
            self.can_sock = messaging.sub_sock('can')
            messages = [("DEBUG", 65)]
            self.can_parser = CANParser('toyota_bsm', messages, 0)

    def _udpate_counter(self, bsm_distance_1, bsm_distance_2, bsm, counter):
        if counter > 0:
            counter -= 1
        else:
            bsm = False
            bsm_distance_1 = 0
            bsm_distance_2 = 0
        return bsm_distance_1, bsm_distance_2, bsm, counter

    def _update_counters(self):
        # left bsm counter
        (self._left_bsm_distance_1,
         self._left_bsm_distance_2,
         self._left_bsm,
         self._left_bsm_counter) = self._udpate_counter(self._left_bsm_distance_1,
                                                        self._left_bsm_distance_2,
                                                        self._left_bsm,
                                                        self._left_bsm_counter)
        # right bsm counter
        (self._right_bsm_distance_1,
         self._right_bsm_distance_2,
         self._right_bsm,
         self._right_bsm_counter) = self._udpate_counter(self._right_bsm_distance_1,
                                                         self._right_bsm_distance_2,
                                                         self._right_bsm,
                                                         self._right_bsm_counter)

    def _update_bsm(self, bsm_distance_1, distance_1, bsm_distance_2, distance_2, bsm, counter):
        if distance_1 != bsm_distance_1:
            bsm_distance_1 = distance_1
            counter = 100
        if distance_2 != bsm_distance_2:
            bsm_distance_2 = distance_2
            counter = 100
        if bsm_distance_1 > 10 or bsm_distance_2 > 10:
            bsm = True

        return bsm_distance_1, bsm_distance_2, bsm, counter

    def _update_bsms(self, side, distance_1, distance_2):
        # Left BSM signal process
        if side == 65:
            (self._left_bsm_distance_1,
             self._left_bsm_distance_2,
             self._left_bsm,
             self._left_bsm_counter) = self._update_bsm(self._left_bsm_distance_1, distance_1,
                                                        self._left_bsm_distance_2, distance_2,
                                                        self._left_bsm, self._left_bsm_counter)
        # Right BSM signal process
        elif side == 66:
            (self._right_bsm_distance_1,
             self._right_bsm_distance_2,
             self._right_bsm,
             self._right_bsm_counter) = self._update_bsm(self._right_bsm_distance_1, distance_1,
                                                         self._right_bsm_distance_2, distance_2,
                                                         self._right_bsm, self._right_bsm_counter)

    def update_states(self, left_bsm, right_bsm):
        self._frame += 1
        if not self._enabled or self._frame < 199:
            return left_bsm, right_bsm

        can_strings = messaging.drain_sock_raw(self.can_sock, wait_for_one=True)
        self.can_parser.update_strings(can_strings)

        distance_1 = self.can_parser.vl["DEBUG"]['BLINDSPOTD1']
        distance_2 = self.can_parser.vl["DEBUG"]['BLINDSPOTD2']
        side = self.can_parser.vl["DEBUG"]['BLINDSPOTSIDE']

        if distance_1 is not None and distance_2 is not None and side is not None:
            self._update_bsms(side, distance_1, distance_2)
            self._update_counters()

    def get_signals(self):
        return self._left_bsm, self._right_bsm