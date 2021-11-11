import numpy as np
import sys
from enum import Enum
from vmu import VoltageMeasurementUnit
from csu import CurrentSourceUnit
from PyQt5 import QtCore
import time


class StateMachine(Enum):
    IDLE = 0
    STOP = 1
    RUN = 2
    PAUSE = 3
    ERROR = 4


class Measurement(QtCore.QThread):
    voltage_data_array = QtCore.pyqtSignal(list)
    current_data_array = QtCore.pyqtSignal(list)
    status_string = QtCore.pyqtSignal(str)
    measurement_finished = QtCore.pyqtSignal(bool)
    time_to_update_plot = QtCore.pyqtSignal(int)

    def __init__(self, cs_device: str = 'NSC5', vs_device: str = 'Lecroy104Xi'):
        QtCore.QThread.__init__(self, None)
        self._current_start = 0.0
        self._step_current = 1e-6
        self._current_points = 101
        self._average_count = 30
        self.delay_before_measurement = 0.01
        self._isRun = False
        self._isPause = False
        self._state_machine_stage = StateMachine.IDLE
        self.cs = CurrentSourceUnit(device=cs_device)
        self.vs = VoltageMeasurementUnit(device=vs_device)
        self.data_list = list()
        self.voltage_values = list()
        self.current_values = list()
        self.voltage_average_list = list()
        self.current_average_list = list()
        self._csu_ranges = self.cs.device_ranges
        self.measurement_mode = 'Default'
        self.vmu_voltage_channel = 1
        self.vmu_current_channel = 2

    def run(self):
        self._state_machine_stage = StateMachine.RUN
        for j in range(self._average_count):
            temp_voltage_values = []
            temp_current_values = []
            if self._state_machine_stage == StateMachine.STOP:
                print('Измерения остановлены пользователем')
                break
            for i in range(self._current_points):
                if self._state_machine_stage == StateMachine.PAUSE:
                    while self._state_machine_stage == StateMachine.RUN:
                        if self._state_machine_stage == StateMachine.STOP:
                            break
                if self._state_machine_stage == StateMachine.STOP:
                    break
                next_current = self._current_start + self._step_current*i
                temp_current_values.append(next_current)
                self.cs.set_current(next_current)
                time.sleep(self.delay_before_measurement)
                temp_voltage_values.append(self.vs.get_data_from_channel(self.voltage_channel))

            self.time_to_update_plot.emit(int((j+1)*100/self.average_count))
            if len(temp_current_values) == self._current_points:
                self.voltage_values.append(temp_voltage_values)
                self.current_values.append(temp_current_values)
                self.voltage_average_list = np.average(self.voltage_values, 0)
        self.measurement_finished.emit(True)
        self._state_machine_stage = StateMachine.STOP

    def stop(self):
        self._isRun = False
        self._state_machine_stage = StateMachine.STOP

    def set_run_on_pause(self):
        self._state_machine_stage = StateMachine.PAUSE
        self._isPause = True

    def get_run_state(self):
        if self._isRun and not self._isPause:
            return self._state_machine_stage, 'measurement in process'
        else:
            return self._state_machine_stage, 'measurement not run or in pause'

    def set_parameters(self, csu_parameters: dict, vmu_parameters: dict):
        self._current_start = csu_parameters['start']
        self._current_points = csu_parameters['points']
        self._step_current = csu_parameters['step']

    @property
    def csu_ranges(self):
        return self._csu_ranges

    @property
    def current_start(self) -> float:
        return self._current_start

    @current_start.setter
    def current_start(self, value: float = 0.0):
        self._current_start = value

    @property
    def average_count(self) -> int:
        return self._average_count

    @average_count.setter
    def average_count(self, value: int = 1):
        if type(value) == int and value > 0:
            self._average_count = value
        else:
            self._average_count = 1

    @property
    def step_current(self) -> float:
        return self._step_current

    @step_current.setter
    def step_current(self, value: float = 1e-6):
        self._step_current = value

    @property
    def current_points(self) -> int:
        return self._current_points

    @current_points.setter
    def current_points(self, value: int = 1):
        self._current_points = value

