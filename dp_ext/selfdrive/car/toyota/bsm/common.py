#!/usr/bin/env python3
# code originally by:
# arne182: https://github.com/arne182
# kumar:   https://github.com/rav4kumar

from openpilot.common.params import Params

ENABLED = Params().get_bool("dp_toyota_enhanced_bsm")