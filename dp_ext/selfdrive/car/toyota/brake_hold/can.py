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

def create_brakehold_command(packer, stock_AEB, cut3frames):
    values = {
        "DSS1GDRV": 1023,
        "PBRTRGR": cut3frames,
    }

    if len(stock_AEB):
        values.update({s: stock_AEB[s] for s in [
            # They are not all necessary since brakehold only sends stopped,
            # however we will leave prepared for the future alternative AEB of the comma.ai
            "DSS1GDRV",
            "DS1STAT2",
            "DS1STBK2",
            "PCSWAR",
            "PCSALM",
            "PCSOPR",
            "PCSABK",
            "PBATRGR",
            "PPTRGR",
            "IBTRGR",
            "CLEXTRGR",
            "IRLT_REQ",
            "BRKHLD",
            "AVSTRGR",
            "VGRSTRGR",
            "PREFILL",
            "PBRTRGR",
            "PCSDIS",
            "PBPREPMP",
        ]})

    return packer.make_can_msg("PRE_COLLISION_2", 0, values)