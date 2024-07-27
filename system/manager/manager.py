#!/usr/bin/env python3
import datetime
import os
import signal
import sys
import traceback

from cereal import log
import cereal.messaging as messaging
import openpilot.system.sentry as sentry
from openpilot.common.params import Params, ParamKeyType
from openpilot.common.text_window import TextWindow
from openpilot.system.hardware import HARDWARE, PC
from openpilot.system.manager.helpers import unblock_stdout, write_onroad_params, save_bootlog
from openpilot.system.manager.process import ensure_running
from openpilot.system.manager.process_config import managed_processes
from openpilot.system.athena.registration import register, UNREGISTERED_DONGLE_ID
from openpilot.common.swaglog import cloudlog, add_file_handler
from openpilot.system.version import get_build_metadata, terms_version, training_version



def manager_init() -> None:
  save_bootlog()

  build_metadata = get_build_metadata()

  params = Params()
  params.clear_all(ParamKeyType.CLEAR_ON_MANAGER_START)
  params.clear_all(ParamKeyType.CLEAR_ON_ONROAD_TRANSITION)
  params.clear_all(ParamKeyType.CLEAR_ON_OFFROAD_TRANSITION)
  if build_metadata.release_channel:
    params.clear_all(ParamKeyType.DEVELOPMENT_ONLY)

  default_params: list[tuple[str, str | bytes]] = [
    ("CompletedTrainingVersion", "0"),
    ("DisengageOnAccelerator", "0"),
    ("GsmMetered", "1"),
    ("HasAcceptedTerms", "0"),
    ("LanguageSetting", "main_en"),
    ("OpenpilotEnabledToggle", "1"),
    ("LongitudinalPersonality", str(log.LongitudinalPersonality.standard)),

    # dp
    ("dp_device_display_off_mode", "0"),
    ("dp_ui_rainbow", "0"),
    ("dp_ui_flight_panel", "0"),
    ("dp_long_de2e", "0"),
    ("dp_long_personality_btn", "0"),
    ("dp_ui_map_full", "0"),
    ("dp_alka", "0"),
    ("dp_device_ip_addr", ""),
    ("dp_vag_sng", "0"),
    ("dp_vehicle_list", ""),
    ("dp_vehicle_assigned", ""),
    ("dp_nav_free_map", "0"),
    ("dp_nav_name", "0"),
    ("dp_nav_traffic", "0"),
    ("dp_toyota_auto_lock", "0"),
    ("dp_toyota_auto_unlock", "0"),
    ("dp_device_disable_onroad_uploads", "0"),
    ("dp_toyota_zss", "0"),
    ("dp_hkg_canfd_low_speed_turn_enhancer", "0"),
    ("dp_long_alt_driving_personality_mode", "0"),
    ("dp_long_alt_driving_personality_speed", "0"),
    ("dp_long_curve_speed_limiter", "0"),
    ("dp_lat_lane_change_assist_mode", "0"),
    ("dp_lat_lane_change_assist_speed", "32"),
    ("dp_lat_lane_change_assist_auto_timer", "1.5"),
    ("dp_lat_road_edge_detection", "0"),
    ("dp_device_disable_logging", "0"),
    ("dp_toyota_pcm_compensation", "0"),
    ("dp_device_is_clone", "0"),
    ("dp_device_dm_unavailable", "0"),
    ("dp_toyota_enhanced_bsm", "0"),
    ("dp_toyota_auto_brake_hold", "0"),
    ("dp_toyota_sng", "0"),
    ("dp_tetoo", "0"),
    ("dp_tetoo_data", ""),
    ("dp_tetoo_gps", ""),
    ("dp_tetoo_speed_camera_taiwan", "0"),
    ("dp_tetoo_speed_camera_threshold", "0"),
    ("dp_long_de2e_road_condition", "1"),  # on by default, depends on dp_long_de2e
    ("dp_device_auto_shutdown", "0"),
    ("dp_device_auto_shutdown_in", "30"),
    ("dp_device_audible_alert_mode", "0"),
    ("dp_long_pal", "0"),
    ("dp_long_pal_freeze", "0"),
    ("dp_long_pal_launch_boost", "0"),
    ("dp_vag_pq_steering_patch", "0"),
    ("dp_lat_lane_priority_mode", "0"),
    ("dp_lat_lane_priority_mode_speed", "0"),
    ("dp_lat_lane_priority_mode_camera_offset", "4"),
  ]
  if not PC:
    default_params.append(("LastUpdateTime", datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat().encode('utf8')))

  params.put("dp_vehicle_list", get_support_vehicle_list())

  if params.get_bool("RecordFrontLock"):
    params.put_bool("RecordFront", True)

  # set unset params
  for k, v in default_params:
    if params.get(k) is None:
      params.put(k, v)

  # Create folders needed for msgq
  try:
    os.mkdir("/dev/shm")
  except FileExistsError:
    pass
  except PermissionError:
    print("WARNING: failed to make /dev/shm")

  # set version params
  params.put("Version", build_metadata.openpilot.version)
  params.put("TermsVersion", terms_version)
  params.put("TrainingVersion", training_version)
  params.put("GitCommit", build_metadata.openpilot.git_commit)
  params.put("GitCommitDate", build_metadata.openpilot.git_commit_date)
  params.put("GitBranch", build_metadata.channel)
  params.put("GitRemote", build_metadata.openpilot.git_origin)
  params.put_bool("IsTestedBranch", build_metadata.tested_channel)
  params.put_bool("IsReleaseBranch", build_metadata.release_channel)

  # set dongle id
  reg_res = register(show_spinner=True)
  if reg_res:
    dongle_id = reg_res
  else:
    serial = params.get("HardwareSerial")
    raise Exception(f"Registration failed for device {serial}")
  os.environ['DONGLE_ID'] = dongle_id  # Needed for swaglog
  os.environ['GIT_ORIGIN'] = build_metadata.openpilot.git_normalized_origin # Needed for swaglog
  os.environ['GIT_BRANCH'] = build_metadata.channel # Needed for swaglog
  os.environ['GIT_COMMIT'] = build_metadata.openpilot.git_commit # Needed for swaglog

  if not build_metadata.openpilot.is_dirty:
    os.environ['CLEAN'] = '1'

  # init logging
  sentry.init(sentry.SentryProject.SELFDRIVE)
  cloudlog.bind_global(dongle_id=dongle_id,
                       version=build_metadata.openpilot.version,
                       origin=build_metadata.openpilot.git_normalized_origin,
                       branch=build_metadata.channel,
                       commit=build_metadata.openpilot.git_commit,
                       dirty=build_metadata.openpilot.is_dirty,
                       device=HARDWARE.get_device_type())

  # preimport all processes
  for p in managed_processes.values():
    p.prepare()


def manager_cleanup() -> None:
  # send signals to kill all procs
  for p in managed_processes.values():
    p.stop(block=False)

  # ensure all are killed
  for p in managed_processes.values():
    p.stop(block=True)

  cloudlog.info("everything is dead")


def manager_thread() -> None:
  cloudlog.bind(daemon="manager")
  cloudlog.info("manager start")
  cloudlog.info({"environ": os.environ})

  params = Params()

  ignore: list[str] = []
  # dp
  dp_device_dm_unavailable = params.get_bool("dp_device_dm_unavailable")
  dp_device_is_clone = params.get_bool("dp_device_is_clone")
  if dp_device_is_clone or dp_device_dm_unavailable:
    ignore += ["manage_athenad", "uploader"]
    if dp_device_dm_unavailable:
      ignore += ["dmonitoringd", "dmonitoringmodeld"]

  if params.get("DongleId", encoding='utf8') in (None, UNREGISTERED_DONGLE_ID):
    ignore += ["manage_athenad", "uploader"]
  if os.getenv("NOBOARD") is not None:
    ignore.append("pandad")
  ignore += [x for x in os.getenv("BLOCK", "").split(",") if len(x) > 0]

  sm = messaging.SubMaster(['deviceState', 'carParams'], poll='deviceState')
  pm = messaging.PubMaster(['managerState'])

  write_onroad_params(False, params)
  ensure_running(managed_processes.values(), False, params=params, CP=sm['carParams'], not_run=ignore)

  started_prev = False

  while True:
    sm.update(1000)

    started = sm['deviceState'].started

    if started and not started_prev:
      params.clear_all(ParamKeyType.CLEAR_ON_ONROAD_TRANSITION)
    elif not started and started_prev:
      params.clear_all(ParamKeyType.CLEAR_ON_OFFROAD_TRANSITION)

    # update onroad params, which drives pandad's safety setter thread
    if started != started_prev:
      write_onroad_params(started, params)

    started_prev = started

    ensure_running(managed_processes.values(), started, params=params, CP=sm['carParams'], not_run=ignore)

    running = ' '.join("{}{}\u001b[0m".format("\u001b[32m" if p.proc.is_alive() else "\u001b[31m", p.name)
                       for p in managed_processes.values() if p.proc)
    print(running)
    cloudlog.debug(running)

    # send managerState
    msg = messaging.new_message('managerState', valid=True)
    msg.managerState.processes = [p.get_process_state_msg() for p in managed_processes.values()]
    pm.send('managerState', msg)

    # Exit main loop when uninstall/shutdown/reboot is needed
    shutdown = False
    for param in ("DoUninstall", "DoShutdown", "DoReboot", "dp_device_reset_conf"):
      if params.get_bool(param):
        if param == "dp_device_reset_conf":
          os.system("rm -fr /data/params/d/dp_*")
        shutdown = True
        params.put("LastManagerExitReason", f"{param} {datetime.datetime.now()}")
        cloudlog.warning(f"Shutting down manager - {param} set")

    if shutdown:
      break


def main() -> None:
  manager_init()
  if os.getenv("PREPAREONLY") is not None:
    return

  # SystemExit on sigterm
  signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))

  try:
    manager_thread()
  except Exception:
    traceback.print_exc()
    sentry.capture_exception()
  finally:
    manager_cleanup()

  params = Params()
  if params.get_bool("DoUninstall"):
    cloudlog.warning("uninstalling")
    HARDWARE.uninstall()
  elif params.get_bool("DoReboot"):
    cloudlog.warning("reboot")
    HARDWARE.reboot()
  elif params.get_bool("DoShutdown"):
    cloudlog.warning("shutdown")
    HARDWARE.shutdown()

def get_support_vehicle_list():
  from openpilot.selfdrive.car.fingerprints import all_known_cars, all_legacy_fingerprint_cars
  import json
  cars = dict({"cars": []})
  list = []
  for car in all_known_cars():
    list.append(str(car))

  for car in all_legacy_fingerprint_cars():
    name = str(car)
    if name not in list:
      list.append(name)
  cars["cars"] = sorted(list)
  return json.dumps(cars)


if __name__ == "__main__":
  unblock_stdout()

  try:
    main()
  except KeyboardInterrupt:
    print("got CTRL-C, exiting")
  except Exception:
    add_file_handler(cloudlog)
    cloudlog.exception("Manager failed to start")

    try:
      managed_processes['ui'].stop()
    except Exception:
      pass

    # Show last 3 lines of traceback
    error = traceback.format_exc(-3)
    error = "Manager failed to start\n\n" + error
    with TextWindow(error) as t:
      t.wait_for_exit()

    raise

  # manual exit because we are forked
  sys.exit(0)
