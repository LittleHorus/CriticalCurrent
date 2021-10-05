from enum import Enum
import matplotlib.pyplot as plt
import numpy as np


class Model:
    def __init__(self):
        self.current_list = list()
        self.voltage_list = list()

    @staticmethod
    def ramp(delta: float = 0.1, mode: str = 'symmetric', points_count: int = 100, *args) -> list:
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

    @staticmethod
    def contact_emul(current: list, critical_current: float = 1e-6, normal_resistance: float = 1.0):
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

    @staticmethod
    def current_emul(current_step: float = 1e-7, length: int = 50, noise_level: float = 5e-8) -> list:
        current_list = [0] * length
        for j in range(length):
            current_list[j] = np.random.normal(0, noise_level, 1)[0] + current_step * j
        return current_list
