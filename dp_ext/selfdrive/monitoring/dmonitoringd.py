#!/usr/bin/env python3
import gc
import time

import cereal.messaging as messaging
from openpilot.common.realtime import set_realtime_priority, DT_DMON
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.events import Events


def dmonitoringd_thread(sm=None, pm=None):
  Params().put_bool("DmModelInitialized", True)
  gc.disable()
  set_realtime_priority(2)

  if pm is None:
    pm = messaging.PubMaster(['driverStateV2', 'driverMonitoringState'])

  # 10Hz <- dmonitoringmodeld
  while True:
    dat = messaging.new_message('driverStateV2')
    dat.driverStateV2.leftDriverData.faceOrientation = [0., 0., 0.]
    dat.driverStateV2.leftDriverData.faceProb = 1.0
    dat.driverStateV2.rightDriverData.faceOrientation = [0., 0., 0.]
    dat.driverStateV2.rightDriverData.faceProb = 1.0
    pm.send('driverStateV2', dat)

    # dmonitoringd output
    dat = messaging.new_message('driverMonitoringState', valid=True)
    dat.driverMonitoringState = {
      "faceDetected": True,
      "isDistracted": False,
      "awarenessStatus": 1.,
    }
    pm.send('driverMonitoringState', dat)
    time.sleep(DT_DMON)

def main(sm=None, pm=None):
  dmonitoringd_thread(sm, pm)


if __name__ == '__main__':
  main()
