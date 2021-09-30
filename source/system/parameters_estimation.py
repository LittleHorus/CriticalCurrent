#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
		temp_res = float()
		for i in range(self.parameters['average_count']):
			temp_part1 = self.parameters['I++'][i] -\
						self.parameters['I+-'][i] -\
						self.parameters['time_step']*self.parameters['current_step']
			temp_part2 = \
				self.parameters['N+-']*self.parameters['time_step'] * \
				(self.parameters['I++'][i] - self.parameters['I+-'][i]) - \
				self.parameters['time_step']*self.parameters['I+-'][i]
			temp_part3 = self.parameters['current_step'] * (self.parameters['I++'][i] - self.parameters['I+-'][i])**2
			temp_res = (temp_part1 * temp_part2) / temp_part3
			estimated_critical_current += temp_res
		return estimated_critical_current

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
