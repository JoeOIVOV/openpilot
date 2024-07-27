#!/usr/bin/env python3
# Code was inspired from Erich Moraga (https://github.com/ErichMoraga/)

from openpilot.common.params import Params

ENABLED = Params().get_bool("dp_toyota_zss")
ALKA = Params().get_bool("dp_alka")