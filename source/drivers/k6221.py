import numpy as np
import visa
import sys


class Device:
    def __init__(self, parent=None):
        self._ip = '192.168.0.70'

    def set_current(self, value):
        pass
    def set_range(self, value):
        pass
    def set_output(self, state):
        pass
    def enable_output(self):
        pass
    def disable_output(self):
        pass
