from enum import Enum
import numpy as np

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
			'time_step': 1e-3,
			'average_count': 1,
			'voltages': list(),
			'currents': list(),
			'I+-': list(),
			'I++': list(),
			'N+-': list(),
			'voltage_threshold': 1e-3
		}

	def estimate_critical_current(self, current_dict: dict, voltage_dict: dict) -> float:
		estimated_critical_current = float()
		temp_hi = float()
		temp_lo = float()

		for i in range(self.parameters['average_count']):
			temp_part1 = self.parameters['I++'][i] -\
						self.parameters['I+-'][i] -\
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

	def contact_emul(self, current: list, critical_current: float = 1e-6, normal_resistance: float = 1.0):
		voltage_response = [0] * len(current)
		first_exceed = 0
		for i in range(len(current)):
			if current[i] < critical_current:
				voltage_response[i] = np.random.normal(0, 5e-9, 1)[0]
			else:
				if first_exceed == 0:
					first_exceed = i
				voltage_response[i] = np.random.normal(0, 5e-9, 1)[0] + normal_resistance * current[i]
		return voltage_response

	def find_smth(self, current, voltage, threshold: float = 1e-3):
		length = len(current)
		i_under = 0.0
		i_upper = 0.0
		index = 0
		for i in range(length):
			if voltage[i] >= threshold:
				i_under = current[i - 1]
				i_upper = current[i]
				index = i - 1
				break
		return i_under, i_upper, index

	def estimate_cc(self, average_count: int = 100, time_step: float = 1e-3, current_step: float = 0.1e-6):
		current = list()
		voltage = list()
		current_previous = list()
		current_exceeded = list()
		index_list = list()
		result = 0.0
		res_up = 0.0
		res_down = 0.0
		for i in range(average_count):
			current_list = [0] * 50
			for j in range(len(current_list)):
				current_list[j] = np.random.normal(0, 10e-8, 1)[0] + current_step * j
			voltage = self.contact_emul(current_list, 4e-6, 1.0)

			cur_pre, cur_up, index = self.find_smth(current_list, voltage, 1e-6)
			current_previous.append(cur_pre)
			current_exceeded.append(cur_up)
			index_list.append(index)

			temp_1 = cur_up - cur_pre - time_step * current_step
			temp_2 = index * time_step * (cur_up - cur_pre) - time_step * cur_pre
			temp_3 = current_step * (cur_up - cur_pre) ** 2
			res_up += (temp_1 * temp_2) / temp_3

			temp_down = ((cur_up - cur_pre - time_step * current_step) / (current_step * (cur_up - cur_pre)))
			res_down += temp_down * temp_down
		result = res_up / res_down
		return result, current_previous, current_exceeded

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
