import numpy as np
import sys
from enum import Enum
from drivers.vmu import VoltageSourceUnit
from drivers.csu import CurrentSourceUnit


class StateMachine(Enum):
    IDLE = 0
    STOP = 1
    RUN = 2
    PAUSE = 3
    ERROR = 4


class Measurement:
    def __init__(self, cs_device: str = 'NSC5', vs_device: str = 'K2182'):
        self._current_start = 0
        self._step_current = 1e-6
        self._current_points = 1
        self._run_state = False
        self._run_pause = False
        self._state_machine_stage = StateMachine.IDLE
        self.cs = CurrentSourceUnit(device=cs_device)
        self.vs = VoltageSourceUnit(device=vs_device)
        self.data_list = list()

    def run(self):
        self._state_machine_stage = StateMachine.RUN
        for i in range(self._current_points):
            if self._state_machine_stage == StateMachine.PAUSE:
                while self._state_machine_stage == StateMachine.RUN:
                    if self._state_machine_stage == StateMachine.STOP:
                        break
            if self._state_machine_stage == StateMachine.STOP:
                break
            next_current = self._current_start + self._step_current*i
            self.cs.set_current(next_current)
            print("current actual point: {}".format(next_current))
            self.data_list.append(self.vs.get_data())
            print('data value: {}'.format(self.data_list[len(self.data_list)-1]))

    def stop(self):
        self._run_state = False
        self._state_machine_stage = StateMachine.STOP

    def set_run_on_pause(self):
        self._state_machine_stage = StateMachine.PAUSE
        self._run_pause = True

    def get_run_state(self):
        if self._run_state is True and self._run_pause is False:
            return self._state_machine_stage, 'measurement in process'

    def set_parameters(self, csu_parameters: dict = {}, vmu_parameters: dict = {}):
        self._current_start = csu_parameters['start']
        self._current_points = csu_parameters['points']
        self._step_current = csu_parameters['step']

    @property
    def current_start(self):
        return self._current_start

    @current_start.setter
    def current_start(self, value: float = 0.0):
        self._current_start = value

    @property
    def step_current(self):
        return self._step_current

    @step_current.setter
    def step_current(self, value: float = 1e-6):
        self._step_current = value

    @property
    def current_points(self):
        return self._current_points

    @current_points.setter
    def current_points(self, value: int = 1):
        self._current_points = value

