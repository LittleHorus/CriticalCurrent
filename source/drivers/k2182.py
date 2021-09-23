import numpy as np
import visa
import sys


class Device:
    def __init__(self):
        self._ip = '192.168.0.71'
        self._voltage_range = '1V'

    @staticmethod
    def get_data(self):
        data = 0
        return data

    @staticmethod
    def set_voltage_range(value: str):
        print(value)

    @staticmethod
    def enable_output(self):
        print("output enabled")

    @staticmethod
    def disable_output(self):
        print("output disabled")

    @property
    def voltage_range(self):
        return self._voltage_range

    @voltage_range.setter
    def voltage_range(self, value: str):
        self._voltage_range = value

