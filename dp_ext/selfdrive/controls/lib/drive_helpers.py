# dp - from original drive_helpers
MIN_SPEED = 1.0
CONTROL_N = 17
# EU guidelines
MAX_LATERAL_JERK = 5.0

# dp - for lat priority mode
from openpilot.common.numpy_fast import interp, clip
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.common.realtime import DT_MDL
def get_lag_adjusted_curvature(CP, v_ego, psis, curvatures): #, curvature_rates):
    if len(psis) != CONTROL_N:
        psis = [0.0]*CONTROL_N
        curvatures = [0.0]*CONTROL_N
        # curvature_rates = [0.0]*CONTROL_N
    v_ego = max(MIN_SPEED, v_ego)

    # TODO this needs more thought, use .2s extra for now to estimate other delays
    delay = CP.steerActuatorDelay + .2

    # MPC can plan to turn the wheel and turn back before t_delay. This means
    # in high delay cases some corrections never even get commanded. So just use
    # psi to calculate a simple linearization of desired curvature
    current_curvature_desired = curvatures[0]
    psi = interp(delay, ModelConstants.T_IDXS[:CONTROL_N], psis)
    average_curvature_desired = psi / (v_ego * delay)
    desired_curvature = 2 * average_curvature_desired - current_curvature_desired

    # This is the "desired rate of the setpoint" not an actual desired rate
    # desired_curvature_rate = curvature_rates[0]
    max_curvature_rate = MAX_LATERAL_JERK / (v_ego**2) # inexact calculation, check https://github.com/commaai/openpilot/pull/24755
    # safe_desired_curvature_rate = clip(desired_curvature_rate,
    #                                    -max_curvature_rate,
    #                                    max_curvature_rate)
    safe_desired_curvature = clip(desired_curvature,
                                  current_curvature_desired - max_curvature_rate * DT_MDL,
                                  current_curvature_desired + max_curvature_rate * DT_MDL)

    return safe_desired_curvature
