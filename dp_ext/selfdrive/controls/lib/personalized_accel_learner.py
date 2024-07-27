import numpy as np
import json
import bisect
from collections import deque
from openpilot.common.params import Params
from openpilot.selfdrive.car.interfaces import ACCEL_MAX

# stock
A_CRUISE_MAX_VALS = [1.6, 1.2, 0.8, 0.6]
A_CRUISE_MAX_BP = [0., 10.0, 25., 40.]


# other constants
SMOOTH_FACTOR = 0.9
LEARNING_RATE = 0.01
MAX_SAMPLES_PER_RANGE = 50

class PersonalizedAccelLearner:
    def __init__(self):
        self.enabled = False
        self._params = Params()
        # params
        self.dp_long_pal_freeze = False
        self.dp_long_pal_launch_boost = 0. # percentage
        self.frame = 0

        self.samples_per_range = self._initialize_variable_samples()

        # The 0.5 m/s intervals up to 2 m/s (roughly 0-7.2 km/h or 0-4.5 mph) allow for very precise control during start-stop traffic.
        # The range from 2 m/s to 15 m/s (7.2-54 km/h or 4.5-33.6 mph) covers most urban driving scenarios.
        # The range from 20 m/s to 40 m/s (72-144 km/h or 44.7-89.5 mph) covers highway driving speeds.
        self.A_MAX_BP = [0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 32.5, 35, 37.5, 40]
        self.profile_size = len(self.A_MAX_BP)

        self.MAX_VALS = np.maximum(0, np.interp(self.A_MAX_BP, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)).tolist()
        self.A_CRUISE_MAX_VALS = self.MAX_VALS.copy()

        self.speed_range_samples = {i: deque(maxlen=MAX_SAMPLES_PER_RANGE) for i in range(self.profile_size)}

        self.speed_range_samples_collected = {i: list for i in range(self.profile_size)}

        self.load_model()

    def _initialize_variable_samples(self):
        return [10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 20, 20, 25, 30, 35, 35, 40, 40, 40]

    def update(self, car_state, lead_present):
        if (not lead_present and
                not car_state.leftBlinker and
                not car_state.rightBlinker and
                car_state.gasPressed and
                abs(car_state.steeringAngleDeg) < 30):

            speed_index = self._get_speed_index(car_state.vEgo)
            self.speed_range_samples[speed_index].append(car_state.aEgo)

            if speed_index < len(self.samples_per_range):
                if len(self.speed_range_samples[speed_index]) >= self.samples_per_range[speed_index]:
                    self._update_cruise_profile_for_index(speed_index)

            self.frame += 1
            if self.frame % 1000 == 0:
                self.save_model()
        # 3 sec
        if self.frame % 60 == 0:
            try:
                if self._params.get_bool("dp_long_pal_reset"):
                    self.MAX_VALS = np.maximum(0, np.interp(self.A_MAX_BP, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)).tolist()
                    self.A_CRUISE_MAX_VALS = self.MAX_VALS.copy()
                    self._params.remove("dp_long_pal_reset")
                    self.save_model()
            except:
                pass

            try:
                self.dp_long_pal_launch_boost = int(self._params.get("dp_long_pal_launch_boost")) * 0.01
            except:
                self.dp_long_pal_launch_boost = 0.

            self.dp_long_pal_freeze = self._params.get_bool("dp_long_pal_freeze")


    def _get_speed_index(self, speed):
        index = bisect.bisect_right(self.A_MAX_BP, speed) - 1
        return max(0, min(index, len(self.A_MAX_BP) - 1))

    def _update_cruise_profile_for_index(self, index):
        samples = list(self.speed_range_samples[index])
        if samples:
            new_sample_val = max(0, float(np.percentile(samples, 95)))

            previous_val = self.A_CRUISE_MAX_VALS[index]
            smoothed_val = SMOOTH_FACTOR * previous_val + (1 - SMOOTH_FACTOR) * new_sample_val

            self.A_CRUISE_MAX_VALS[index] = previous_val * (1 - LEARNING_RATE) + smoothed_val * LEARNING_RATE

    def get_max_accel(self, v_ego, STOCK_BP, STOCK_VALS):
        if self.enabled:
            val = np.interp(v_ego, self.A_MAX_BP, self.A_CRUISE_MAX_VALS)
        else:
            val = np.interp(v_ego, STOCK_BP, STOCK_VALS)
        if self.dp_long_pal_launch_boost > 0. and v_ego <= 5.:
            # limit to ACCEL_MAX
            val = min(val * (1 + self.dp_long_pal_launch_boost), ACCEL_MAX)
        return val

    def set_enabled(self, enabled):
        self.enabled = enabled

    def save_model(self):
        data = {
            'bp': self.A_MAX_BP,
            'vals': self._numpy_to_list(self.A_CRUISE_MAX_VALS)
        }
        self._params.put("dp_long_pal_vals", json.dumps(data))

    def load_model(self):
        try:
          params_val = self._params.get("dp_long_pal_vals")
        except:
          params_val = None
        if params_val is not None:
            data = json.loads(params_val)
            self.A_CRUISE_MAX_VALS = np.maximum(0, np.interp(self.A_MAX_BP, data.get('bp'), data.get('vals'))).tolist()

    def _numpy_to_list(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, list):
            return [self._numpy_to_list(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._numpy_to_list(value) for key, value in obj.items()}
        else:
            return obj

    def pac_thread(self):
        from cereal.messaging import SubMaster

        sm = SubMaster(['carState', 'radarState'])

        while True:
            sm.update()
            if sm.updated['carState']:
                self.update(sm['carState'], sm['radarState'].leadOne.status and sm['carState'].vEgo > 0. and sm['radarState'].leadOne.dRel / sm['carState'].vEgo < 2.5)

def main():
    pac = PersonalizedAccelLearner()
    pac.pac_thread()

if __name__ == "__main__":
    main()