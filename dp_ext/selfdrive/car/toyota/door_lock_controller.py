#!/usr/bin/env python3
from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params


GearShifter = car.CarState.GearShifter
UNLOCK_CMD = b'\x40\x05\x30\x11\x00\x40\x00\x00'
LOCK_CMD = b'\x40\x05\x30\x11\x00\x80\x00\x00'
LOCK_AT_SPEED = 10 * CV.KPH_TO_MS


class DoorLockController:

    def __init__(self):
        params = Params()
        self._dp_toyota_auto_lock = params.get_bool("dp_toyota_auto_lock")
        self._dp_toyota_auto_unlock = params.get_bool("dp_toyota_auto_unlock")
        self._dp_toyota_auto_lock_once = False
        self._gear_prev = GearShifter.park


    def process(self, gear, v_ego, door_open):
        # dp - door auto lock / unlock logic
        # thanks to AlexandreSato & cydia2020
        # https://github.com/AlexandreSato/animalpilot/blob/personal/doors.py
        message = []
        if not door_open:
            if gear == GearShifter.park and gear != self._gear_prev:
                if self._dp_toyota_auto_unlock:
                    message = [0x750, UNLOCK_CMD, 0]
                self._dp_toyota_auto_lock_once = False
            elif gear == GearShifter.drive and not self._dp_toyota_auto_lock_once and v_ego >= LOCK_AT_SPEED:
                if self._dp_toyota_auto_lock:
                    message = [0x750, LOCK_CMD, 0]
                self._dp_toyota_auto_lock_once = True
            self._gear_prev = gear
        return message