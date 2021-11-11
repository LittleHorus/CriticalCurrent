from enum import Enum


class EstimateParameters(Enum):
    CriticalCurrent = 0
    Resistance = 1
    GapVoltage = 2


class Estimation:

    def _init_(self, param_type: str = 'critical_current'):
        self._data = 0.0
        self.result_value = 0.0
        self.parameters = {
            'current_step': 1e-9,
            'time_step': 1,
            'average_count': 1,
            'voltages': list(),
            'currents': list(),
            'I+-': list(),
            'I++': list(),
            'N+-': list(),
            'voltage_threshold': 1e-6
        }

    def estimate_critical_current(self, current_dict: dict, voltage_dict: dict) -> float:
        temp_hi = float()
        temp_lo = float()

        for i in range(self.parameters['average_count']):
            temp_part1 = self.parameters['I++'][i] - \
                         self.parameters['I+-'][i] - \
                         self.parameters['time_step']*self.parameters['current_step']
            temp_part2 = \
                self.parameters['N+-']*self.parameters['time_step'] * \
                (self.parameters['I++'][i] - self.parameters['I+-'][i]) - \
                self.parameters['time_step']*self.parameters['I+-'][i]
            temp_part3 = self.parameters['current_step'] * (self.parameters['I++'][i] - self.parameters['I+-'][i])**2
            temp_hi += temp_part1 * temp_part2
            temp_lo += temp_part3
        estimated_critical_current = temp_hi / temp_lo
        return estimated_critical_current

    @staticmethod
    def find_smth(current, voltage, threshold: float = 1e-3):
        length = len(current)
        i_under = 0.0
        i_upper = 0.0
        v_under = 0.0
        v_upper = 0.0
        index = 0
        for i in range(length):
            if voltage[i] >= threshold:
                i_under = current[i - 1]
                i_upper = current[i]
                v_under = voltage[i - 1]
                v_upper = voltage[i]
                index = i - 1
                break
        return i_under, i_upper, index, v_under, v_upper

    @staticmethod
    def estimate_cc(
            current: list, voltage: list, current_step: float = 0.1e-6, time_step: float = 1.0,
            threshold: float = 1.8e-6):
        current_previous = list()
        current_exceeded = list()
        index_list = list()
        voltage_previous = list()
        voltage_exceeded = list()
        res_up = 0.0
        res_down = 0.0
        for i in range(len(current)):
            current_list = current[i]
            voltage_list = voltage[i]

            cur_pre, cur_up, index, vol_pre, vol_up = Estimation.find_smth(current_list, voltage_list, threshold)
            current_previous.append(cur_pre)
            current_exceeded.append(cur_up)
            voltage_previous.append(vol_pre)
            voltage_exceeded.append(vol_up)
            index_list.append(index)

            temp_1 = cur_up - cur_pre - time_step * current_step
            temp_2 = float(index) * time_step * (cur_up - cur_pre) - time_step * cur_pre
            temp_3 = current_step * (cur_up - cur_pre) ** 2
            res_up += (temp_1 * temp_2) / temp_3

            temp_down = ((cur_up - cur_pre - time_step * current_step) / (current_step * (cur_up - cur_pre)))**2
            res_down += temp_down
        result = res_up / res_down
        return result, current_previous, current_exceeded, voltage_previous, voltage_exceeded, index_list

    @staticmethod
    def estimate_cc_f2(
            current: list, voltage: list,
            current_step: float = 0.1e-6, time_step: float = 1e-6, threshold: float = 1.8e-6):
        c_before = list()
        c_after = list()
        v_before = list()
        v_after = list()
        threshold_exceeded_index = list()
        current_sum = list()
        current_total = 0.0
        for i in range(len(current)):
            current_list = current[i]
            voltage_list = voltage[i]
            cur_pre, cur_up, index, vol_pre, vol_up = Estimation.find_smth(current_list, voltage_list, threshold)
            c_before.append(cur_pre)
            c_after.append(cur_up)
            v_before.append(vol_pre)
            v_after.append(vol_up)
            threshold_exceeded_index.append(index)
            current_sum.append(cur_pre+cur_up)
            current_total += cur_pre+cur_up
        result = current_total / (2*len(current))
        return result, c_before, c_after, v_before, v_after, threshold_exceeded_index

    @staticmethod
    def find_threshold_exceed(data: list, threshold: float) -> int:
        result = 0  # index
        for i in range(len(data)):
            if data[i] > threshold:
                result = i
                break
        return result

    @staticmethod
    def threshold_array(data: list, threshold: float) -> list:
        result = list()
        for i in range(len(data)):
            result.append(Estimation.find_threshold_exceed(data[i], threshold))
        return result

    def set_parameters(self):
        index_list = Estimation.threshold_array(self.parameters['voltages'], self.parameters['voltage_threshold'])
        for i in range(self.parameters['average_count']):
            if index_list[i] == 0:
                raise Exception('ThresholdError')
            self.parameters['I++'] = self.parameters['currents'][i][index_list[i]]
            self.parameters['I+-'] = self.parameters['currents'][i][index_list[i]-1]
            self.parameters['N+-'] = index_list[i]-1

    def set_data(self, voltage_list, current_list):
        if len(voltage_list) != len(current_list):
            raise Exception('DataAlignmentError')
        self.parameters['voltages'] = voltage_list
        self.parameters['currents'] = current_list
        self.parameters['average_count'] = len(voltage_list)

    def update_data(self, voltage_list, current_list):
        if len(voltage_list) != len(current_list):
            raise Exception('DataAlignmentError')
        self.parameters['voltages'].append(voltage_list)
        self.parameters['currents'].append(current_list)
        self.parameters['average_count'] = len(self.parameters['voltages'])
