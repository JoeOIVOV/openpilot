#!/usr/bin/env python3
from cereal import car
from openpilot.common.params import Params
from openpilot.common.realtime import Priority, config_realtime_process
from openpilot.dp_ext.selfdrive.controls.lib.lateral_mpc_lane_planner import LateralMpcLanePlanner
import cereal.messaging as messaging

def latpland_thread():
    config_realtime_process(5, Priority.CTRL_LOW)

    params = Params()
    with car.CarParams.from_bytes(params.get("CarParams", block=True)) as msg:
        CP = msg

    lmlp = LateralMpcLanePlanner(CP)

    pm = messaging.PubMaster(['lateralPlan'])
    sm = messaging.SubMaster(['carState', 'modelV2'], poll='modelV2')

    while True:
        sm.update()

        if sm.updated['modelV2']:
            plan_send = messaging.new_message('lateralPlan')
            plan_send.valid = sm.all_checks(service_list=['carState', 'modelV2'])
            lat_plan = plan_send.lateralPlan

            lmlp.update_md(sm['modelV2'])
            lmlp.update_v_ego(sm['carState'].vEgo)

            if lmlp.should_activate():
                lmlp.update()

                lat_plan.psis = lmlp.get_psis()
                lat_plan.curvatures = lmlp.get_curvatures()
                # lat_plan.curvatureRates = lmlp.get_curvature_rates()

            lat_plan.useLaneLines = lmlp.is_active()

            pm.send('lateralPlan', plan_send)


def main():
    latpland_thread()

if __name__ == "__main__":
    main()