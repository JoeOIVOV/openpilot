#!/usr/bin/env python3
# code originally by:
# Alexandre Sato: https://github.com/AlexandreSato

from openpilot.common.params import Params

ENABLED = Params().get_bool("dp_toyota_auto_brake_hold")