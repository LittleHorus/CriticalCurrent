import socket
import crcmod
from ctypes import (Union, Array, c_uint8, c_float, cdll, CDLL)
from enum import Enum
from ctypes import *
import visa
import ncs5
import k6221


class CurrentSourceUnit:
    def __init__(self, device: str='NCS5'):
        self._ch_count = 1
        self._range_enum = {'50mA': [-50e-3, 50e3, 1e-6], '10mA': [-10e-3, 10e-3, 100e-9], '1mA': [-1e-3, 1e-3, 10e-9],
                            '100uA': [-100e-6, 100e-6, 1e-9], '10uA': [-10e-6, 10e-6, 100e-12],
                            '1uA': [-1e-6, 1e-6, 10e-12]}
        self._connection_state = 'False'
        self._current = 0
        self._device = device
        if self._device == 'NCS5' or 'ncs5' or 'ncs':
            self.current_src = ncs5.Device()
        elif self._device == 'Keithley 6221':
            self.current_src = k6221.Device()
        else:
            raise Exception('DeviceSupportError')

    @property
    def current(self):
        return self._current

    @property
    def connection_state(self):
        return self._connection_state

    @property
    def ch_count(self):
        return self._ch_count

    @property
    def range_enum(self):
        return self._range_enum

    @property
    def device(self):
        return self._device

    @current.setter
    def current(self, value: float):
        self._current = value

    @connection_state.setter
    def connection_state(self, value: bool):
        self._connection_state = value

    @ch_count.setter
    def ch_count(self, value: int):
        self._ch_count = value

    @range_enum.setter
    def range_enum(self, value: str):
        self._range_enum = value

    @device.setter
    def device(self, value: str):
        self._device = value

    def set_current(self, current: float):
        self.current_src.set_current(current)

    def enable_output(self):
        self.current_src.enable_output()

    def disable_output(self):
        self.current_src.disable_output()

    def set_output_state(self, state: bool):
        self.current_src.set_output_state(state)

    def set_range(self, range_value: str):
        self.current_src.set_range(range_value)


