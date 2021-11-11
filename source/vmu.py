import drivers.Lecroy104Xi as Lecroy104Xi


class VoltageMeasurementUnit:
    def __init__(self, device: str = 'Lecroy104Xi'):
        self._device = device
        self.default_channel = 1
        print(self._device, type(self._device))
        if self._device == 'Lecroy104Xi':
            self.voltage_unit = Lecroy104Xi.Lecroy()
        else:
            raise Exception("DeviceSupportError")

    def get_data(self):
        return self.get_data_from_channel(self.default_channel)

    def set_voltage_range(self, value: str):
        self.set_channel_range(self.default_channel, value)

    def get_data_from_channel(self, channel: int):
        return self.voltage_unit.get_data_from_channel(channel)

    def set_channel_range(self, channel: int, ch_range):
        self.voltage_unit.set_channel_range(channel, range)

    @property
    def device(self):
        return self._device


