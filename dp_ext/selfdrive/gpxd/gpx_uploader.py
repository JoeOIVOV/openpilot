#!/usr/bin/env python3

import os
import time
from openpilot.common.params import Params
from openpilot.system.version import get_version, get_branch
from openpilot.common.realtime import set_core_affinity, set_realtime_priority

# for uploader
from openpilot.system.loggerd.xattr_cache import getxattr, setxattr
import glob
import requests
import json

from openpilot.dp_ext.utils import is_private_ip

# customisable values
GPX_LOG_PATH = '/data/media/0/gpx_logs/'
LOG_HERTZ = 1/10 # 0.1 Hz = 10 sec, higher for higher accuracy, 10hz seems fine

# uploader
UPLOAD_ATTR_NAME = 'user.upload'
UPLOAD_ATTR_VALUE = b'1'
LOG_PATH = '/data/media/0/gpx_logs/'

# osm api
API_HEADER = {'Authorization': 'Bearer 2pvUyXfk9vizuh7PwQFSEYBtFWcM-Pu7vxApUjSA0fc'}
VERSION_URL = 'https://api.openstreetmap.org/api/versions'
UPLOAD_URL = 'https://api.openstreetmap.org/api/0.6/gpx/create'

_DEBUG = False

def _debug(msg):
  if not _DEBUG:
    return
  print(msg, flush=True)

class GpxUploader():
  def __init__(self):
    self._delete_after_upload = True #not Params().get_bool('dp_gpxd')
    self._car_model = "Unknown Vehicle"
    self._version = get_version()
    self._branch = get_branch()

  def _identify_vehicle(self):
    # read model from LiveParameters
    params = Params().get("LiveParameters")
    if params is not None:
      params = json.loads(params)
      self._car_model = params.get('carFingerprint', self._car_model)
    _debug("GpxUploader init - _delete_after_upload = %s" % self._delete_after_upload)
    _debug("GpxUploader init - _car_model = %s" % self._car_model)

  def _is_online(self):
    try:
      r = requests.get(VERSION_URL, headers=API_HEADER)
      _debug("is_online? status_code = %s" % r.status_code)
      return r.status_code >= 200
    except Exception:
      return False

  def _get_is_uploaded(self, filename):
    result = getxattr(filename, UPLOAD_ATTR_NAME) is not None
    _debug("%s is uploaded: %s" % (filename, result))
    return result

  def _set_is_uploaded(self, filename):
    _debug("%s set to uploaded" % filename)
    setxattr(filename, UPLOAD_ATTR_NAME, UPLOAD_ATTR_VALUE)

  def _get_files(self):
    return sorted( filter( os.path.isfile, glob.glob(LOG_PATH + '*') ) )

  def _get_files_to_be_uploaded(self):
    files = self._get_files()
    files_to_be_uploaded = []
    for file in files:
      if not self._get_is_uploaded(file):
        files_to_be_uploaded.append(file)
    return files_to_be_uploaded

  def _do_upload(self, filename):
    fn = os.path.basename(filename)
    data = {
      'description': f"Routes from dragonpilot {self._branch} / {self._version} ({self._car_model}).",
      'visibility': 'identifiable'
    }
    try:
      if not is_private_ip():
        return False
      with open(filename, 'rb') as file:
        files = {"file": (fn, file)}
        r = requests.post(UPLOAD_URL, files=files, data=data, headers=API_HEADER)
      _debug("do_upload - %s - %s" % (filename, r.status_code))
      return r.status_code == 200
    except Exception as e:
      print(f"Error in _do_upload: {e}")
      return False

  def run(self):
    # give it few seconds before we start running the process
    # only identify vehicle once
    time.sleep(10)
    self._identify_vehicle()
    while True:
      is_offroad = Params().get_bool("IsOffroad")
      files = self._get_files_to_be_uploaded()
      if len(files) == 0:
        if is_offroad and self._delete_after_upload:
          for file in self._get_files():
            os.remove(file)
        _debug("run - no files, clean stash")
      elif not self._is_online() and self._delete_after_upload:
        _debug("run - not online & delete_after_upload")
        for file in files:
          os.remove(file)
      else:
        for file in files:
          if self._do_upload(file):
            if self._delete_after_upload:
              _debug("run - _delete_after_upload")
              os.remove(file)
            else:
              _debug("run - set_is_uploaded")
              self._set_is_uploaded(file)
      time.sleep(60)

def gpx_uploader_thread():
  set_core_affinity([0, 1, 2, 3])
  set_realtime_priority(1)
  gpx_uploader = GpxUploader()
  gpx_uploader.run()

def main():
  gpx_uploader_thread()

if __name__ == "__main__":
  main()
