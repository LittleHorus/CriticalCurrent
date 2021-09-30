#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import Enum
import matplotlib.pyplot as plt


class Model:
	def __init__(self):
		self.current_list = list()
		self.voltage_list = list()

	@staticmethod
	def ramp(delta: float = 0.1, mode: str = 'symmetric', points_count: int = 100) -> list:
		result = list()
		if mode == 'symmetric':
			if points_count % 2:  # odd 1,3,5
				center = int(points_count / 2)
				print('center: {}'.format(center))
				for i in range(points_count):
					if i <= center:
						result.append(i*delta)
					else:
						result.append(delta*center + delta*(center-i))

			else:
				center_pos = int(points_count / 2)
				for i in range(center_pos):
					result.append(i*delta)
				for i in range(center_pos):
					result.append((center_pos*delta - (i+1)*delta))
		if mode == 'up':
			for i in range(points_count):
				result.append(i*delta)
		if mode == 'down':
			for i in range(points_count):
				result.append(-i*delta)
		return result
