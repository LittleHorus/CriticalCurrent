import socket
import numpy as np
import sys


class Device:
    def __init__(self, ip: str = '192.168.0.71', port: int = 1234):
        self._ip = ip
        self._port = port
        self._voltage_range = '1V'
        self.gpib = PrologixGPIBEthernet(self._ip, self._port)
        self._gpib_address = 17

    def connect(self):
        self.gpib.connect()
        self.gpib.select(self._gpib_address)

    def disconnect(self):
        self.gpib.close()

    def idn_query(self):
        result = self.gpib.query('*IDN?')
        print(result)
        return result

    def set_channel(self, channel = 1):
        if channel == 1:
            self.gpib.write('SENS:CHAN 1')
        if channel == 2:
            self.gpib.write('SENS:CHAN 2')

    def set_voltage_digits(self, digit: int = 8):
        self.gpib.write('SENS:VOLT:DIG {}'.format(digit))

    def set_npl_cycles(self, cycles: int = 1):
        self.gpib.write('SENS:VOLT:NPLC {}'.format(cycles))

    def set_function(self, func_: str = 'VOLT'):
        self.gpib.write('SENS:FUNC {}'.format(func_))

    def set_range(self, channel_range: int = 10):
        self.gpib.write('SENS:VOLT:CHAN:RANG:UPP {}'.format(channel_range))

    def get_data(self):
        return self.gpib.query('SENS:DATA:FRESh?')

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


class PrologixGPIBEthernet:

    def __init__(self, ip: str = '192.168.0.70', port: int = 1234):
        self._ip = ip
        self._port = port
        self._timeout = 1
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM,
                                  socket.IPPROTO_TCP)
        self.sock.settimeout(self._timeout)

    def connect(self):
        self.sock.connect((self._ip, self._port))
        self._setup()

    def close(self):
        self.sock.close()

    def select(self, addr):
        self._send('++addr %i' % int(addr))

    def write(self, cmd):
        self._send(cmd)

    def read(self, bytes_count: int = 1024):
        self._send('read_eoi')
        return self._recv(bytes_count)

    def query(self, cmd, buffer_size=1024*1024):
        self.write(cmd)
        return self.read(buffer_size)

    def _setup(self):
        self._send('++mode 1')  # set device to controller mode
        self._send('++auto 0')  # disable read after write
        self._send('++read_tmo_ms %i' % int(self._timeout*01e3))  # set GPIB timeout
        self._send('++eos 3')  # do not required CR or LF appended to GPIB data

    def _send(self, value):
        encoded_value = ('%s\n' % value).encode('ascii')
        self.sock.send(encoded_value)

    def _recv(self, bytes_count):
        raw_data = self.sock.recv(bytes_count)
        return raw_data.decode('ascii')


