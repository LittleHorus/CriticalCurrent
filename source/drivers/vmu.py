import socket
import crcmod
from ctypes import (Union, Array, c_uint8, c_float, cdll, CDLL)
from enum import Enum
from ctypes import *
import visa

import k2182


class VoltageSourceUnit:
    def __init__(self, device_name: str = 'K2182'):
        self._device = device_name
        if self._device == "K2182":
            self.voltage_source = k2182.Device()
        else:
            raise Exception("DeviceSupportError")

    def get_data(self):
        return self.voltage_source.get_data()

    def set_voltage_range(self, value: str):
        self.voltage_source.set_voltage_range(value)

    @property
    def device(self):
        return self._device


