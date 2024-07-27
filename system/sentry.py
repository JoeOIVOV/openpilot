import os
import traceback
from datetime import datetime
"""Install exception handler for process crash."""
import sentry_sdk
from enum import Enum
from sentry_sdk.integrations.threading import ThreadingIntegration

from openpilot.common.params import Params
# from openpilot.system.athena.registration import is_registered_device
from openpilot.system.hardware import HARDWARE #, PC
from openpilot.common.swaglog import cloudlog
from openpilot.system.version import get_build_metadata, get_version
from openpilot.system.hardware.hw import Paths
from cereal import car


class SentryProject(Enum):
  # python project
  SELFDRIVE = "https://980a0cba712a4c3593c33c78a12446e1@o273754.ingest.sentry.io/1488600"
  # native project
  SELFDRIVE_NATIVE = "https://980a0cba712a4c3593c33c78a12446e1@o273754.ingest.sentry.io/1488600"


CRASH_DIR = Paths.crash_root()
IP_ADDRESS = "{{auto}}"


def report_tombstone(fn: str, message: str, contents: str) -> None:
  cloudlog.error({'tombstone': message})

  with sentry_sdk.configure_scope() as scope:
    bind_user()
    scope.set_extra("tombstone_fn", fn)
    scope.set_extra("tombstone", contents)
    sentry_sdk.capture_message(message=message)
    sentry_sdk.flush()


def capture_exception(*args, **kwargs) -> None:
  save_exception(traceback.format_exc())
  cloudlog.error("crash", exc_info=kwargs.get('exc_info', 1))

  try:
    bind_user()
    sentry_sdk.capture_exception(*args, **kwargs)
    sentry_sdk.flush()  # https://github.com/getsentry/sentry-python/issues/291
  except Exception:
    cloudlog.exception("sentry exception")

def save_exception(exc_text: str) -> None:
  if not os.path.exists(CRASH_DIR):
    os.makedirs(CRASH_DIR)

  files = [
    os.path.join(CRASH_DIR, datetime.now().strftime('%Y-%m-%d--%H-%M-%S.log')),
    os.path.join(CRASH_DIR, 'error.txt')
  ]

  for file in files:
    with open(file, 'w') as f:
      if file.endswith("error.txt"):
        lines = exc_text.splitlines()[-3:]
        f.write("\n".join(lines))
      else:
        f.write(exc_text)
  print('Logged current crash to {}'.format(files))

def bind_user() -> None:
  dongle_id, gitname, _ = get_properties()
  sentry_sdk.set_user({"id": dongle_id, "ip_address": IP_ADDRESS, "name": gitname})

def capture_warning(warning_string: str) -> None:
  bind_user()
  sentry_sdk.capture_message(warning_string, level='warning')
  sentry_sdk.flush()

def capture_info(info_string: str) -> None:
  bind_user()
  sentry_sdk.capture_message(info_string, level='info')
  sentry_sdk.flush()

def set_tag(key: str, value: str) -> None:
  sentry_sdk.set_tag(key, value)

def get_tags() -> tuple[str, str, str]:
  params = Params()
  hardware_serial: str = params.get("HardwareSerial", encoding='utf-8') or ""
  gitname: str = params.get("GithubUsername", encoding='utf-8') or ""
  dongle_id: str = params.get("DongleId", encoding='utf-8') or f"UNREGISTERED-{hardware_serial}"

  vehicle_model = "mock"
  cached_params = params.get("CarParamsCache")
  if cached_params is not None:
    cached_params = car.CarParams.from_bytes(cached_params)
    vehicle_model = cached_params.carName

  return dongle_id, gitname, vehicle_model


def init(project: SentryProject) -> bool:
  build_metadata = get_build_metadata()
  # forks like to mess with this, so double check
  #comma_remote = build_metadata.openpilot.comma_remote and "commaai" in build_metadata.openpilot.git_origin
  #if not comma_remote or not is_registered_device() or PC:
  #  return False

  dongle_id, gitname, vehicle_model = get_tags()

  env = "release" if build_metadata.tested_channel else "master"
  dongle_id = Params().get("DongleId", encoding='utf-8')

  integrations = []
  if project == SentryProject.SELFDRIVE:
    integrations.append(ThreadingIntegration(propagate_hub=True))

  sentry_sdk.init(project.value,
                  default_integrations=False,
                  release=get_version(),
                  integrations=integrations,
                  traces_sample_rate=1.0,
                  max_value_length=8192,
                  send_default_pii=True, # for IP
                  environment=env)

  build_metadata = get_build_metadata()

  sentry_sdk.set_user({"id": dongle_id})
  sentry_sdk.set_user({"ip_address": IP_ADDRESS})
  sentry_sdk.set_user({"name": gitname})
  sentry_sdk.set_tag("dirty", build_metadata.openpilot.is_dirty)
  sentry_sdk.set_tag("origin", build_metadata.openpilot.git_origin)
  sentry_sdk.set_tag("branch", build_metadata.channel)
  sentry_sdk.set_tag("commit", build_metadata.openpilot.git_commit)
  sentry_sdk.set_tag("device", HARDWARE.get_device_type())
  sentry_sdk.set_tag("vehicle", vehicle_model)

  if project == SentryProject.SELFDRIVE:
    sentry_sdk.Hub.current.start_session()

  return True
