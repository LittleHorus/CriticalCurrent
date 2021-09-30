import pyvisa as visa


class Device:
    def __init__(self, ip: str = '192.168.0.70'):
        self._ip = ip
        self.rm = visa.ResourceManager('@py')
        self._current_ranges = ['2nA', '20nA', '200nA',
                                '2uA', '20uA', '200uA',
                                '2mA', '20mA', '200mA']
        try:
            self.instrument = self.rm.open_resource("TCPIP0::{}::INSTR".format(self._ip))
        except visa.errors.VisaIOError:
            print('K6221 is not present in the system')

    def connect(self):
        self.instrument = self.rm.open_resource("TCPIP0::{}::INSTR".format(self._ip))

    def disconnect(self):
        self.instrument.close()

    def set_current(self, value: float):
        self.instrument.write('CURR {}'.format(value))

    def set_range(self, current_range: str = '20mA'):
        self.instrument.write('CURR:RANG {}'.format(current_range))

    def set_compliance(self, value: int = 10):
        self.instrument.write('CURR:COMP {}'.format(value))

    def set_analog_filter_state(self, state: bool = False):
        if state is True:
            self.instrument.write('CURR:FILT ON')
        else:
            self.instrument.write('CURR:FILT OFF')

    def enable_output(self):
        self.instrument.write('OUTP ON')

    def disable_output(self):
        self.instrument.write('OUTP OFF')

    def set_output_state(self, state: bool):
        if state is True:
            self.enable_output()
        else:
            self.disable_output()

    @property
    def current_ranges(self):
        return self._current_ranges

    @current_ranges.setter
    def current_ranges(self, value: str):
        print('access denied')

