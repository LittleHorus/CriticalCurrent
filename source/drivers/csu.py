import socket
import crcmod
from ctypes import (Union, Array, c_uint8, c_float, cdll, CDLL)
from enum import Enum
from ctypes import *
import visa
import ncs5
import k6221


class CurrentSourceUnit:
    def __init__(self, parent=None):
        self._ch_count = 1
        self._range_enum = {'50mA': [-50e-3, 50e3, 1e-6], '10mA': [-10e-3, 10e-3, 100e-9], '1mA': [-1e-3, 1e-3, 10e-9],
                            '100uA': [-100e-6, 100e-6, 1e-9], '10uA': [-10e-6, 10e-6, 100e-12],
                            '1uA': [-1e-6, 1e-6, 10e-12]}
        self._connection_state = 'False'
        self._current = 0
        self._device = 'NCS5'
        if self._device == 'NCS5' or 'ncs5' or 'ncs':
            self.current_src = ncs5.NCS5()
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
    def current(self, value):
        self._current = value

    @connection_state.setter
    def connection_state(self, value):
        self._connection_state = value

    @ch_count.setter
    def ch_count(self, value):
        self._ch_count = value

    @range_enum.setter
    def range_enum(self, value):
        self._range_enum = value

    @device.setter
    def device(self, value):
        self._device = value


    def set_current(self, channel, current):
        if self._device == 'NCS5':
            ncs5.set_current(channel, current)
        else:
            print("unsupported device")


    def enable_output(self):
        if self._device == 'NCS5':
            ncs5.set_enable()
        else:
            print("unsupported device")


    def disable_output(self, channel):
        if self._device == 'NCS5':
            ncs5.set_disable(channel)
        else:
            print("unsupported device")


    def set_output_state(self, channel, state):
        if self._device == 'NCS5':
            if state == True or state == 1 or state == '1' or state == 'ON':
                ncs5.set_enable(channel)
            elif state == False or state == 0 or state == '0' or state == 'OFF':
                ncs5.set_disable(channel)
            else:
                print("unsupported parameter {}".format(state))
        else:
            print("unsupported device")


    def set_range(self, channel, ch_range):
        if self._device == 'NCS5':
            ncs5.set_range(channel, ch_range)
        else:
            print("unsupported device")
