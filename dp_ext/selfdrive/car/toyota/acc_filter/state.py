#!/usr/bin/env python3
# This is only required for SDSU, not Radar CAN Filter

from openpilot.selfdrive.car.toyota.values import ToyotaFlags

from opendbc.can.parser import CANParser
from cereal import messaging
from openpilot.selfdrive.pandad import can_capnp_to_list

class ACCFilterState:
    def __init__(self, CP):
        self._has_sdsu_flag = CP.flags & ToyotaFlags.SMART_DSU
        self._has_radar_can_filter_flag = CP.flags & ToyotaFlags.RADAR_CAN_FILTER

        self._use_sdsu_not_radar_filter = self._has_sdsu_flag and not self._has_radar_can_filter_flag

        if self._use_sdsu_not_radar_filter:
            self.can_sock = messaging.sub_sock('can')
            messages = [("SDSU", 100)]
            self.can_parser = CANParser('toyota_sdsu', messages, 0)

    def get_distance_button_states(self, prev_distance_button, distance_button):
        if not self._use_sdsu_not_radar_filter:
            return prev_distance_button, distance_button

        can_strings = messaging.drain_sock_raw(self.can_sock, wait_for_one=True)
        can_list = can_capnp_to_list(can_strings)
        self.can_parser.update_strings(can_list)

        prev_distance_button = distance_button
        return prev_distance_button, self.can_parser.vl["SDSU"]['FD_BUTTON']