import numpy as np
import visa
import sys


class Device:
    def __init__(self, parent=None):
        self._ip = '192.168.0.70'

    def set_current(self, value: float):
        print(value)

    def set_range(self, value):
        pass

    def enable_output(self):
        pass

    def disable_output(self):
        pass

    @staticmethod
    def set_output_state(self, state: bool):
        print(state)
