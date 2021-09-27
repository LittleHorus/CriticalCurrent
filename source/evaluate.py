import numpy as np
import matplotlib.pyplot as plt


class Estimation:
    def __init__(self):
        self._data = list()
        self._critical_current_value = 0.0
        self._currents = list()
        self._voltages = list()

    def estimate(self, data: list,  mode: str = 'CriticalCurrent') -> float:
        result = 0.0
        if mode == 'CriticalCurrent':
            result = self.estimate_critical_current(data)
        if mode == 'GapVoltage':
            result = self.estimate_gap_voltage(data)
        return result

    @staticmethod
    def estimate_critical_current(data: list) -> float:
        print("input data: {}".format(data))
        return 0.0

    @staticmethod
    def estimate_gap_voltage(data: list) -> float:
        print('input data: {}'.format(data))
        return 0.0

    @staticmethod
    def load_from_file(filepath):
        return np.load(filepath)

    @staticmethod
    def save_to_file(filepath, data):
        np.save(filepath, data)

    @property
    def data(self) -> list:
        return self._data

    @data.setter
    def data(self, value: list):
        self._data = value

    @property
    def critical_current_value(self) -> float:
        return self._critical_current_value

    @critical_current_value.setter
    def critical_current_value(self, value: float):
        self._critical_current_value = value

    @property
    def currents(self) -> list:
        return self._currents

    @currents.setter
    def currents(self, value: list):
        self._currents = value

    @property
    def voltages(self) -> list:
        return self._voltages

    @voltages.setter
    def voltages(self, value: list):
        self._voltages = value
