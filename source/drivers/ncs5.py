import socket
import crcmod
from ctypes import (Union, Array, c_uint8, c_float, cdll, CDLL)
from enum import Enum
from ctypes import *


class U8Array(Array):
	_type_ = c_uint8
	_length_ = 4


class FType(Union):
	_fields_ = ("float", c_float), ("char", U8Array)


class Device:
	def __init__(self, parent=None):
		self.sock = socket.socket()
		self._connection_status = False
		self._device_address = 0xc1
		self._default_channel = 1

	def connect(self, dist_address=('192.168.0.77', 7)):
		self.sock.connect(dist_address)

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
	def float_to4bytes(float_data: float = 0.0):
		temp_data = FType()
		temp_data.float = float_data
		return temp_data.char[:]

	@staticmethod
	def byte_array_to_float(data_array: list, offset: int = 0):
		temp_data = FType()
		temp_data.char[:] = (data_array[0+offset], data_array[1+offset], data_array[2+offset], data_array[3+offset])
		return temp_data.float

	def ch_output_enable(self, channel: int = 1):
		temp_data = [self._device_address, 0x70, 0x71, 0x71, 0x71, 0x71, 0x71, 0x7f, 0x7f, 0x7f]
		temp_data[1] = 0x70 | channel
		temp_data[9] = self.crc8_custom(temp_data, 9)
		self.send_via_socket(temp_data)

	def ch_output_disable(self, channel: int = 1):
		temp_data = [self._device_address, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x7f, 0x7f, 0x7f]
		temp_data[1] = 0x70 | channel
		temp_data[9] = self.crc8_custom(temp_data, 9)
		self.send_via_socket(temp_data)

	def ch_set_range(self, channel: int = 1, channel_range: str = '1uA'):
		# 1uA 10uA 100uA 1mA 10mA 50mA
		temp_data = [self._device_address, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7f, 0x7f, 0x7f]
		temp_data[1] = 0x60 | channel
		if channel_range == '1uA' or channel_range == 1e-6:
			temp_data[channel+1] = 0x60
		elif channel_range == '10uA' or channel_range == 1e-5:
			temp_data[channel+1] = 0x61
		elif channel_range == '100uA' or channel_range == 1e-4:
			temp_data[channel+1] = 0x62
		elif channel_range == '1mA' or channel_range == 1e-3:
			temp_data[channel+1] = 0x63
		elif channel_range == '10mA' or channel_range == 1e-2:
			temp_data[channel+1] = 0x64
		elif channel_range == '50mA' or channel_range == 5e-2:
			temp_data[channel+1] = 0x65
		else:
			temp_data[channel+1] = 0x60  # 1uA range
		temp_data[9] = self.crc8_custom(temp_data, 9)
		self.send_via_socket(temp_data)

	def ch_set_current(self, channel: int = 1, current: float = 0.0):
		float_4_bytes = []*4
		float_4_bytes = self.float_to4bytes(current)
		temp_data = [self._device_address, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0xD0, 0x7f]
		temp_data[1] = 0xD0 | channel
		temp_data[2] = float_4_bytes[0]
		temp_data[3] = float_4_bytes[1]
		temp_data[4] = float_4_bytes[2]
		temp_data[5] = float_4_bytes[3]
		temp_data[9] = self.crc8_custom(temp_data, 9)
		self.send_via_socket(temp_data)
		
	def send_via_socket(self, data: list):
		self.sock.send(bytearray(data))
		return self.sock.recv(10)

	def set_current(self, current: float):
		self.ch_set_current(self._default_channel, current)

	def enable_output(self):
		self.ch_output_enable(self._default_channel)

	def disable_output(self):
		self.ch_output_disable(self._default_channel)

	def set_output_state(self, state: bool):
		if state is True:
			self.ch_output_enable(self._default_channel)
		else:
			self.ch_output_disable(self._default_channel)

	def set_range(self, value: str):
		self.ch_set_range(self._default_channel, value)

	@property
	def connection_status(self):
		return self._connection_status

	@connection_status.setter
	def connection_status(self, value: bool):
		if value is False or value is True:
			self._connection_status = value

	@property
	def device_address(self):
		return self._device_address

	@device_address.setter
	def device_address(self, value: int):
		if type(value) == int and 0 < value < 16:
			self._device_address = value | 0xc0
			
	@property
	def default_channel(self):
		return self._default_channel
	
	@default_channel.setter
	def default_channel(self, value: int):
		if type(value) == int and 0 < value < 16:
			self._default_channel = value 

