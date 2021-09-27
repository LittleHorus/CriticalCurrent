import pyvisa as visa


class Device:
    def __init__(self, ip: str = '192.168.0.70'):
        self._ip = ip
        self.rm = visa.ResourceManager('@py')
        self.instrument = self.rm.open_resource("TCPIP0::{}::INSTR".format(self._ip))

    def connect(self):
        pass
    
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

