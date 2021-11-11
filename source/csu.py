import drivers.ncs5 as ncs5


class CurrentSourceUnit:
    def __init__(self, device: str = 'NCS5', addr: str = '192.168.0.77'):
        self._ch_count = 1
        self._range_enum = {'50мА': [-50e-3, 50e3, 1e-6], '10мА': [-10e-3, 10e-3, 100e-9], '1мА': [-1e-3, 1e-3, 10e-9],
                            '100мкА': [-100e-6, 100e-6, 1e-9], '10мкА': [-10e-6, 10e-6, 100e-12],
                            '1мкА': [-1e-6, 1e-6, 10e-12]}
        self._connection_state = 'False'
        self._current = 0
        self._device = device

        if self._device == 'NCS5' or self._device == 'ncs5' or self._device == 'ncs':
            self.current_src = ncs5.Device()
        else:
            raise Exception('DeviceSupportError')
        self._device_ranges = self.current_src.current_ranges

    @property
    def device_ranges(self) -> list:
        return self._device_ranges

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

    def connect(self):
        self.current_src.connect()

    def disconnect(self):
        self.current_src.disconnect()


