#!/usr/bin/env python3
# code originally by:
# Alexandre Sato: https://github.com/AlexandreSato

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