import socket
import crcmod
from ctypes import (Union, Array, c_uint8, c_float, cdll, CDLL)
from enum import Enum
from ctypes import *


class uint8_array(Array):
	_type_ = c_uint8
	_length_ = 4


class f_type(Union):
	_fields_ = ("float", c_float), ("char", uint8_array)


class NCS5():
	def __init__(self, parent = None):
		self.sock = socket.socket()
		self._connection_status = False
		self._device_address = 0xc1
		self._default_channel = 1

	def connect(self, dist_addr=('192.168.0.77', 7)):
		self.sock.connect(dist_addr)

	@staticmethod
	def crc8_custom(data, length=9):
		crc = c_uint8(0xff)
		i = c_uint32(0)
		for j in range(length):
			dt = c_uint8(data[j])
			crc.value ^= dt.value
			for k in range(8):
				if (crc.value & 0x80) != 0:
					crc.value = (crc.value << 1) ^ 0x31
				else:
					crc.value <<= 1  # crc.value<<1
		return crc.value

	@staticmethod
	def float_to4bytes(float_data):
		temp_data = f_type()
		temp_data.float = float_data
		return temp_data.char[:]


	def byteArray_toFloat(self, data_array, offset = 0):
		temp_data = f_type()
		temp_data.char[:] = (data_array[0+offset],data_array[1+offset],data_array[2+offset],data_array[3+offset])
		return temp_data.float

	def ch_output_enable(self, channel = 1):
		tData = [self._device_address, 0x70, 0x71, 0x71, 0x71, 0x71, 0x71, 0x7f, 0x7f, 0x7f]
		tData[1] = 0x70 | channel
		tData[9] = self.crc8_custom(tData, 9)
		self.send_via_socket(tData)

	def ch_output_disable(self, channel = 1):
		tData = [self._device_address, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x7f, 0x7f, 0x7f]
		tData[1] = 0x70 | channel
		tData[9] = self.crc8_custom(tData, 9)
		self.send_via_socket(tData)

	def ch_set_range(self, channel=1, channel_range='1uA'):
		# 1uA 10uA 100uA 1mA 10mA 50mA
		tData = [self._device_address, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7f, 0x7f, 0x7f]
		tData[1] = 0x60 | channel
		if channel_range == '1uA' or channel_range == 1e-6:
			tData[channel+1] = 0x60
		elif channel_range == '10uA' or channel_range == 1e-5:
			tData[channel+1] = 0x61
		elif channel_range == '100uA' or channel_range == 1e-4:
			tData[channel+1] = 0x62
		elif channel_range == '1mA' or channel_range == 1e-3:
			tData[channel+1] = 0x63
		elif channel_range == '10mA' or channel_range == 1e-2:
			tData[channel+1] = 0x64
		elif channel_range == '50mA' or channel_range == 5e-2:
			tData[channel+1] = 0x65
		else:
			tData[channel+1] = 0x60  # 1uA range
		tData[9] = self.crc8_custom(tData, 9)
		self.send_via_socket(tData)

	def ch_set_current(self, channel=1, current=0.0):
		tFloat4bytes = []*4
		tFloat4bytes = self.float_to4bytes(current)
		tData = [self._device_address, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0x7f]
		tData[1] = 0xD0 | channel
		tData[2] = tFloat4bytes[0]
		tData[3] = tFloat4bytes[1]
		tData[4] = tFloat4bytes[2]
		tData[5] = tFloat4bytes[3]
		tData[9] = self.crc8_custom(tData, 9)
		self.send_via_socket(tData)
		
	def send_via_socket(self, data):
		self.sock.send(bytearray(data))
		return self.sock.recv(10)

	def set_current(self, current):
		self.ch_set_current(self._default_channel, current)

	def enable_output(self):
		self.ch_output_enable(self._default_channel)

	def disable_output(self):
		self.ch_output_disable(self._default_channel)

	def set_range(self, value):
		self.ch_set_range(self._default_channel, value)

	@property
	def connection_status(self):
		return self._connection_status

	@connection_status.setter
	def connection_status(self, value: object):
		if value is False or value is True:
			self._connection_status = value

	@property
	def device_address(self):
		return self._device_address

	@device_address.setter
	def device_address(self, value):
		if type(value) == int and 0 < value < 16:
			self._device_address = value | 0xc0
			
	@property
	def default_channel(self):
		return self._default_channel
	
	@default_channel.setter
	def default_channel(self, value):
		if type(value) == int and 0 < value < 16:
			self._default_channel = value 

