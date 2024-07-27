#!/usr/bin/env python3

import numpy as np
from openpilot.common.realtime import DT_MDL
from openpilot.common.numpy_fast import interp
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N, MIN_SPEED, get_speed_error
from openpilot.common.conversions import Conversions as CV
from cereal import log

from openpilot.dp_ext.selfdrive.controls.lib.lateral_mpc_lib.lat_mpc import LateralMpc
from openpilot.dp_ext.selfdrive.controls.lib.lateral_mpc_lib.lat_mpc import N as LAT_MPC_N
from openpilot.dp_ext.selfdrive.controls.lib.lane_planner import LanePlanner, TRAJECTORY_SIZE, CAMERA_OFFSET

PATH_COST = 1.0
LATERAL_MOTION_COST = 0.11
LATERAL_ACCEL_COST = 0.0
LATERAL_JERK_COST = 0.04
# Extreme steering rate is unpleasant, even
# when it does not cause bad jerk.
# TODO this cost should be lowered when low
# speed lateral control is stable on all cars
STEERING_RATE_COST = 700.0

LaneChangeState = log.LaneChangeState

class LateralMpcLanePlanner:
  def __init__(self, CP):
    self.params = Params()
    self.md = None
    self.frame = 0

    self._is_enabled = Params().get_bool("dp_lat_lane_priority_mode")
    self._dp_lat_lane_priority_mode_speed = 0.
    self._dp_lat_lane_priority_mode_active = False
    self._dp_lat_lane_priority_mode_active_prev = False
    self._dp_lat_lane_priority_mode_camera_offset = CAMERA_OFFSET
    self.LP = LanePlanner()

    # Vehicle model parameters used to calculate lateral movement of car
    self.factor1 = CP.wheelbase - CP.centerToFront
    self.factor2 = (CP.centerToFront * CP.mass) / (CP.wheelbase * CP.tireStiffnessRear)
    self.solution_invalid_cnt = 0

    self.path_xyz = np.zeros((TRAJECTORY_SIZE, 3))
    self.velocity_xyz = np.zeros((TRAJECTORY_SIZE, 3))
    self.plan_yaw = np.zeros((TRAJECTORY_SIZE,))
    self.plan_yaw_rate = np.zeros((TRAJECTORY_SIZE,))
    self.t_idxs = np.arange(TRAJECTORY_SIZE)
    self.y_pts = np.zeros((TRAJECTORY_SIZE,))
    self.v_plan = np.zeros((TRAJECTORY_SIZE,))
    self.v_ego = MIN_SPEED

    self.lat_mpc = LateralMpc()
    self.reset_mpc(np.zeros(4))

    self.v_ego_car = 0.0
    self.lll_prob = 0.
    self.rll_prob = 0.

  def reset_mpc(self, x0=None):
    if x0 is None:
      x0 = np.zeros(4)
    self.x0 = x0
    self.lat_mpc.reset(x0=self.x0)

  def parse_model(self):
    # Parse model predictions
    if len(self.md.position.x) == TRAJECTORY_SIZE and len(self.md.orientation.x) == TRAJECTORY_SIZE:
      self.path_xyz = np.column_stack([self.md.position.x, self.md.position.y, self.md.position.z])
      self.t_idxs = np.array(self.md.position.t)
      self.plan_yaw = np.array(self.md.orientation.z)
      self.plan_yaw_rate = np.array(self.md.orientationRate.z)
      self.velocity_xyz = np.column_stack([self.md.velocity.x, self.md.velocity.y, self.md.velocity.z])
      car_speed = np.linalg.norm(self.velocity_xyz, axis=1) - get_speed_error(self.md, self.v_ego_car)
      self.v_plan = np.clip(car_speed, MIN_SPEED, np.inf)
      self.v_ego = self.v_plan[0]

    # let LanePlanner to read model
    self.LP.parse_model(self.md)

  def update_md(self, md):
    self.md = md

  def update_v_ego(self, v_ego):
    self.v_ego_car = v_ego

    # 3 secs
    if self.frame % 60 == 0:
      try:
        self._dp_lat_lane_priority_mode_speed = int(self.params.get("dp_lat_lane_priority_mode_speed")) * CV.KPH_TO_MS
      except (ValueError, TypeError):
        self._dp_lat_lane_priority_mode_speed = 0.

      try:
        self._dp_lat_lane_priority_mode_camera_offset = int(self.params.get("dp_lat_lane_priority_mode_camera_offset")) * 0.01
      except (ValueError, TypeError):
        self._dp_lat_lane_priority_mode_camera_offset = CAMERA_OFFSET
      self.LP.update_offsets(self._dp_lat_lane_priority_mode_camera_offset)

    self.frame += 1

  def update(self):
    self.parse_model()

    # getting d path from LanePlanner instead of model
    path_xyz = self.LP.get_d_path(self.v_ego_car, self.t_idxs, self.path_xyz)

    self.lat_mpc.set_weights(PATH_COST, LATERAL_MOTION_COST,
                             LATERAL_ACCEL_COST, LATERAL_JERK_COST,
                             STEERING_RATE_COST)

    y_pts = path_xyz[:LAT_MPC_N+1, 1]
    heading_pts = self.plan_yaw[:LAT_MPC_N+1]
    yaw_rate_pts = self.plan_yaw_rate[:LAT_MPC_N+1]
    self.y_pts = y_pts

    assert len(y_pts) == LAT_MPC_N + 1
    assert len(heading_pts) == LAT_MPC_N + 1
    assert len(yaw_rate_pts) == LAT_MPC_N + 1
    lateral_factor = np.clip(self.factor1 - (self.factor2 * self.v_plan**2), 0.0, np.inf)
    p = np.column_stack([self.v_plan, lateral_factor])
    self.lat_mpc.run(self.x0,
                     p,
                     y_pts,
                     heading_pts,
                     yaw_rate_pts)
    # init state for next iteration
    # mpc.u_sol is the desired second derivative of psi given x0 curv state.
    # with x0[3] = measured_yaw_rate, this would be the actual desired yaw rate.
    # instead, interpolate x_sol so that x0[3] is the desired yaw rate for lat_control.
    self.x0[3] = interp(DT_MDL, self.t_idxs[:LAT_MPC_N + 1], self.lat_mpc.x_sol[:, 3])

    #  Check for infeasible MPC solution
    mpc_nans = np.isnan(self.lat_mpc.x_sol[:, 3]).any()
    if mpc_nans or self.lat_mpc.solution_status != 0:
      self.reset_mpc()

    if self.lat_mpc.cost > 1e6 or mpc_nans:
      self.solution_invalid_cnt += 1
    else:
      self.solution_invalid_cnt = 0

  def should_activate(self):
    # decide what mode should we use
    # lll_prob = md.laneLineProbs[1]
    # rll_prob = md.laneLineProbs[2]
    if self.md.laneLineProbs[1] < 0.3 or self.md.laneLineProbs[2] < 0.3:
      self._dp_lat_lane_priority_mode_active = False
    if self.md.laneLineProbs[1] > 0.6 and self.md.laneLineProbs[2] > 0.6:
      self._dp_lat_lane_priority_mode_active = True

    # when blinker is on
    if self.md.meta.laneChangeState != LaneChangeState.off:
      self._dp_lat_lane_priority_mode_active = False

    # when drive speed is below set speed
    if self._dp_lat_lane_priority_mode_active and self._dp_lat_lane_priority_mode_speed > 0 and self.v_ego_car < self._dp_lat_lane_priority_mode_speed:
      self._dp_lat_lane_priority_mode_active = False

    # reset mpc when first active
    if self._dp_lat_lane_priority_mode_active and not self._dp_lat_lane_priority_mode_active_prev:
      self.reset_mpc()

    self._dp_lat_lane_priority_mode_active_prev = self._dp_lat_lane_priority_mode_active
    return self._dp_lat_lane_priority_mode_active

  def set_enabled(self, enabled: bool) -> None:
    self._is_enabled = enabled

  def is_enabled(self):
    return self._is_enabled

  def set_speed(self, speed: float) -> None:
    self._dp_lat_lane_priority_mode_speed = speed

  def get_psis(self):
    return self.lat_mpc.x_sol[0:CONTROL_N, 2].tolist()

  def get_curvatures(self):
    return (self.lat_mpc.x_sol[0:CONTROL_N, 3]/self.v_ego).tolist()

  # def get_curvature_rates(self):
  #   return [float(x/self.v_ego) for x in self.lat_mpc.u_sol[0:CONTROL_N - 1]] + [0.0]
  #
  def is_active(self):
    return self._is_enabled and self._dp_lat_lane_priority_mode_active