#!/usr/bin/env python3
# code originally by:
# Alexandre Sato: https://github.com/AlexandreSato

from openpilot.dp_ext.selfdrive.car.toyota.brake_hold.common import ENABLED
from opendbc.can.parser import CANParser
from cereal import car, messaging

class BrakeHoldState:
    def __init__(self, supported_vehicles):
        # AleSato's automatic brakehold
        self.time_to_brakehold = 100 * 3   # 3 seconds stopped to activate
        self.GearShifter = car.CarState.GearShifter # avoid Rear and Park gears
        self.stock_aeb = {} # need for CS
        self.brakehold_condition_satisfied = False
        self.brakehold_condition_counter = 0
        self.reset_brakehold = False
        self.prev_brakePressed = True
        self.brakehold_governor = False # need for CS

        self._enabled = ENABLED and supported_vehicles
        if self._enabled:
            self.can_sock = messaging.sub_sock('can')
            messages = [("PRE_COLLISION_2", 33)]
            self.can_parser = CANParser('toyota_brake_hold', messages, 0)

    def update_states(self, standstill, cruise_state, gas_pressed, brake_pressed, gear_shifter):
        if not self._enabled:
            return
        can_strings = messaging.drain_sock_raw(self.can_sock, wait_for_one=True)
        self.can_parser.update_strings(can_strings)

        self.stock_aeb = self.can_parser.vl["PRE_COLLISION_2"]
        self.brakehold_condition_satisfied =  (standstill and cruise_state.available and not gas_pressed and \
                                               not cruise_state.enabled and not (gear_shifter in (self.GearShifter.reverse, \
                                                                                                        self.GearShifter.park)))

        if self.brakehold_condition_satisfied:
            if self.brakehold_condition_counter > self.time_to_brakehold and not self.reset_brakehold:
                self.brakehold_governor = True
            else:
                self.brakehold_governor = False

            if not self.prev_brakePressed and brake_pressed: # disable automatic brakehold in second brakePress
                self.reset_brakehold = True
            self.brakehold_condition_counter += 1
        else:
            self.brakehold_governor = False
            self.reset_brakehold = False
            self.brakehold_condition_counter = 0

        self.prev_brakePressed = brake_pressed

    def get_values(self):
        return self.brakehold_governor, self.stock_aeb