import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QWhatsThis
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QTimer

import re
import numpy as np
import os
from time import gmtime, strftime
import time
import traceback
import socket
import sys
import array
import struct
import binascii
import types
from measurement import Measurement
from system.plot_widget import MplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from system.load_settings import LoadSettings
from system.parameters_estimation import Estimation

__version__ = '1.0.1'
__author__ = 'Dmitriy'

from PyQt5.QtWidgets import QMessageBox


class CommonWindow(QtWidgets.QWidget):  # QMainWindow QtWidgets.QWidget
    """Класс основного окна программы"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.common_path = ''
        try:
            self.common_path = os.path.dirname(os.path.abspath('lqce_estimate.py'))
            print('dir path: {}'.format(self.common_path))
        except Exception as exc:
            print('get filepath failed: {}'.format(exc))

        self.open_settings = LoadSettings()
        self.open_settings.open_file()
        self.open_settings.processing_file_data()

        self.measurement_thread = Measurement(self.open_settings.csu_device, self.open_settings.vmu_device)
        att_csu_ranges = self.measurement_thread.csu_ranges

        vertical_size = 30
        horizontal_size = 80

        self.table_previous_row = 0
        self.table_current_row = 0

        self.sc = MplCanvas(self, width=12, height=6, dpi=100)
        self.sc.plot_x_label = 'Ток, А'
        self.sc.plot_y_label = "Напряжение, В"
        self.sc.plot_title = 'Вольт-Амперная характеристика'
        toolbar = NavigationToolbar(self.sc, self)
        self.sc.setMinimumWidth(700)

        self.tab_wdg = Tabs(self, horizontal_size, vertical_size, att_csu_ranges)

        self.isRunMeasurement = False
        self.isCurrentSourceConnected = False

        self.vbox_level1 = QtWidgets.QVBoxLayout()
        self.vbox_level2 = QtWidgets.QVBoxLayout()
        self.hbox_level1 = QtWidgets.QHBoxLayout()
        self.hbox_level1.addWidget(self.tab_wdg)
        self.vbox_level2.addWidget(toolbar, alignment=Qt.AlignHCenter)
        self.vbox_level2.addWidget(self.sc)
        self.vbox_level2.addWidget((QtWidgets.QLabel("")), 2)

        self.hbox_level1.insertLayout(1, self.vbox_level2)
        self.vbox_level1.insertLayout(0, self.hbox_level1)
        self.vbox_level1.addWidget(QtWidgets.QLabel(""))

        self.setLayout(self.vbox_level1)
        self.show()
        self.tab_wdg.btn_csu_connect.clicked.connect(self.on_connect_csu)
        self.tab_wdg.btn_vmu_connect.clicked.connect(self.on_connect_vmu)
        self.tab_wdg.btn_load_file.clicked.connect(self.on_load_from_file)
        self.tab_wdg.btn_run_measurement.clicked.connect(self.on_run_measurement)
        self.tab_wdg.btn_save_result.clicked.connect(self.on_save_result)

        self.measurement_thread.measurement_finished.connect(self.on_measurement_finished)
        self.measurement_thread.time_to_update_plot.connect(self.on_update_plot_proc)

        self.current_from_file = list()
        self.voltage_from_file = list()

        self.tab_wdg.table_of_params.itemClicked.connect(self.on_change_active_row)
        self.list_of_wdg_state = [
            self.tab_wdg.box_measurement_mode, self.tab_wdg.led_measurement_average,
            self.tab_wdg.led_sampling_time, self.tab_wdg.btn_csu_connect, self.tab_wdg.btn_vmu_connect,
            self.tab_wdg.led_start_current, self.tab_wdg.led_step_current, self.tab_wdg.led_points_current,
            self.tab_wdg.box_vmu_ch_voltage, self.tab_wdg.box_vmu_ch_current, self.tab_wdg.cmb_current_range,
            self.tab_wdg.box_vmu_flt_current, self.tab_wdg.box_vmu_flt_voltage, self.tab_wdg.btn_save_result]

    def on_update_plot_proc(self, value):
        index_data = len(self.measurement_thread.voltage_values)-1
        self.sc.plot(self.measurement_thread.current_values[0], self.measurement_thread.voltage_average_list)
        self.tab_wdg.pbar.setValue(value)
        if self.tab_wdg.box_measurement_mode.currentText() == 'Оценивание':
            print('critical current: {}'.format(
                Estimation.estimate_cc_f2(self.measurement_thread.current_values,
                                          self.measurement_thread.voltage_values, 1e-6, 1e-3, 100)[0]
            ))

    def on_save_result(self):
        try:
            np.save(
                '{}\\{}_data.npy'.format(self.common_path, strftime("%H%M")),
                [self.measurement_thread.current_values, self.measurement_thread.voltage_values])
        except Exception as exc:
            print('Exception: {}'.format(exc))

    def on_measurement_finished(self, value: bool):
        print('Окончание измерения: {}'.format(value))
        self.on_run_measurement(True)

    def on_run_measurement(self, stop_signal):
        if self.isRunMeasurement or stop_signal:
            self.tab_wdg.btn_run_measurement.setText('Запустить\n измерение')
            self.isRunMeasurement = False
            self.measurement_thread.stop()
            for i in range(len(self.list_of_wdg_state)):
                self.list_of_wdg_state[i].setDisabled(False)
        else:
            if self.tab_wdg.box_measurement_mode.currentText() == 'Стандартный':
                self.measurement_thread.measurement_mode = 'Default'
            else:
                self.measurement_thread.measurement_mode = 'Estimation'
            for i in range(len(self.list_of_wdg_state)):
                self.list_of_wdg_state[i].setDisabled(True)
            self.measurement_thread.average_count = int(self.tab_wdg.led_measurement_average.text())
            self.measurement_thread.current_points = int(self.tab_wdg.led_points_current.text())
            self.measurement_thread.current_start = float(self.tab_wdg.led_start_current.text())
            self.measurement_thread.step_current = float(self.tab_wdg.led_step_current.text())
            self.measurement_thread.delay_before_measurement = float(self.tab_wdg.led_sampling_time.text())
            self.measurement_thread.voltage_values = []
            self.measurement_thread.current_values = []
            self.measurement_thread.voltage_average_list = []
            self.tab_wdg.btn_run_measurement.setText('Остановить\n измерение')
            self.isRunMeasurement = True
            self.measurement_thread.start()

    def on_change_active_row(self):
        self.table_previous_row = self.table_current_row
        self.table_current_row = self.tab_wdg.table_of_params.currentRow()
        print('current row: {} prev: {}'.format(self.table_current_row, self.table_previous_row))
        try:
            self.tab_wdg.table_of_params.selectRow(self.table_current_row)
            if self.table_current_row < len(self.current_from_file):
                self.sc.plot(self.current_from_file[self.table_current_row], self.voltage_from_file[self.table_current_row])
        except Exception as exc:
            print("Exception: {}".format(exc))

    def update_estimation(self, current_list, voltage_list):
        tuple_data = Estimation.estimate_cc_f2(current_list, voltage_list, 25e-9, 1e-7)

        est_current = tuple_data[0]
        table_ipm = tuple_data[1]
        table_ipp = tuple_data[2]
        table_vpm = tuple_data[3]
        table_vpp = tuple_data[4]
        table_i = tuple_data[5]

        for i in range(len(table_i)):
            self.tab_wdg.table_of_params.setItem(i, 0, QtWidgets.QTableWidgetItem("{:.3e}".format(table_ipm[i])))
            self.tab_wdg.table_of_params.item(i, 0).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            self.tab_wdg.table_of_params.setItem(i, 1, QtWidgets.QTableWidgetItem("{:.3e}".format(table_ipp[i])))
            self.tab_wdg.table_of_params.item(i, 1).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            self.tab_wdg.table_of_params.setItem(
                i, 2, QtWidgets.QTableWidgetItem("{:.3e}".format(table_vpm[i])))
            self.tab_wdg.table_of_params.item(i, 2).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            self.tab_wdg.table_of_params.setItem(
                i, 3, QtWidgets.QTableWidgetItem("{:.3e}".format(table_vpp[i])))
            self.tab_wdg.table_of_params.item(i, 3).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            self.tab_wdg.table_of_params.setItem(i, 4, QtWidgets.QTableWidgetItem("{}".format(table_i[i])))
            self.tab_wdg.table_of_params.item(i, 4).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        print('estimate current: {}'.format(est_current))
        self.tab_wdg.estimate_value_led.setText('{:.3e}'.format(est_current))
        self.sc.plot(self.current_from_file[0], self.voltage_from_file[0])

    def on_load_from_file(self):
        file_type = 'prn'
        filename = ''
        result_data = list()
        result_current = list()
        result_voltage = list()
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open file', self.common_path,
                "Mathcad(*prn);;Text files(*.txt);;Numpy(*.npy);;", "Mathcad (*.prn)")[0]
            if bool(re.search('.prn', filename)):
                file_type = 'prn'
            if bool(re.search('.npy', filename)):
                file_type = 'npy'
            if bool(re.search('.txt', filename)):
                file_type = 'txt'
        except Exception as exc:
            print('Exception: {}'.format(exc))
        try:
            if file_type == 'txt':
                result_data = self.load_txt(filename)
            elif file_type == 'npy':
                result_data = self.load_npy(filename)
            elif file_type == 'prn':
                result_current = self.load_prn(filename, filename_type='FULL_PATH')
                filename = QtWidgets.QFileDialog.getOpenFileName(
                    self, 'Open voltage values file', self.common_path, "Mathcad(*prn)", "Mathcad (*.prn)")[0]
                result_voltage = self.load_prn(filename, filename_type='FULL_PATH')
                result_data.append(result_current)
                result_data.append(result_voltage)
                self.current_from_file = result_current
                self.voltage_from_file = result_voltage
                self.sc.plot(list(self.current_from_file[0]), list(self.voltage_from_file[0]))
                self.update_estimation(self.current_from_file, self.voltage_from_file)
            else:
                raise Exception('UnknownDataTypeError')
        except Exception as exc:
            print(exc)
        return result_data

    @staticmethod
    def display_error(error, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("{}".format(error))
        msg.setInformativeText('{}'.format(text))
        msg.setWindowTitle("Error")
        msg.exec_()

    @staticmethod
    def save_result_to_file(path, data):
        print("save to file {}\\{}".format(path, data))

    def on_connect_csu(self):
        try:
            if self.isCurrentSourceConnected:
                self.tab_wdg.btn_csu_connect.setText('Отключить')
                self.isCurrentSourceConnected = True
            else:
                self.tab_wdg.btn_csu_connect.setText('Подключить')
                self.isCurrentSourceConnected = False
                print('connect to csu device[{}]'.format(self.open_settings.csu_device))
        except Exception as exc:
            print(exc)
            traceback.print_exc()

    def on_connect_vmu(self):
        try:
            print('connect to vmu device[{}]'.format(self.open_settings.vmu_device))
        except Exception as exc:
            print(exc)
            traceback.print_exc()

    def load_prn(self, filename='current_data_0.prn', filename_type='FULL_PATH'):
        if filename_type == 'NAME_ONLY':
            with open("{}\\data\\{}".format(self.common_path, filename), "r") as file_:
                data = file_.readlines()
                data_result = self.convert_prn(data)
                return data_result
        if filename_type == 'FULL_PATH':
            with open(filename, "r") as file_:
                data = file_.readlines()
                data_result = self.convert_prn(data)
                return data_result

    def load_npy(self, filename):
        return np.load(filename)

    def load_txt(self, filename):
        return np.loadtxt(filename, float, delimiter=',')

    def convert_prn(self, prn_data):
        data = list()
        if bool(re.search(r',', prn_data[0])):
            data = list()
            for i in range(len(prn_data)):
                res = re.sub(r',', r".", prn_data[i])
                t_data = np.fromstring(res, dtype=float, sep=' ')
                data.append(t_data)
            return data
        else:
            for i in range(len(prn_data)):
                res = re.sub(r'(e-[0-9]{3})', r"\1 ", prn_data[i])
                res = re.sub(r'\s\s', r" ", res)
                t_data = np.fromstring(res, dtype=float, sep=' ')
                data.append(t_data)
        return data


class Tabs(QtWidgets.QWidget):
    def __init__(self, parent=None, widget_width=80, widget_height=30, att_csu_ranges: list = None,
                 att_vmu_ranges: list = None):
        if att_csu_ranges is None:
            att_csu_ranges = ['']
        if att_vmu_ranges is None:
            att_vmu_ranges = ['']
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.__widget_width = widget_width
        self.__widget_height = widget_height

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tabs.setMinimumSize(600, 600)
        self.tabs.setMaximumWidth(700)
        self.tabs.resize(600, 600)

        self.tabs.addTab(self.tab1, "Измерения")
        self.tabs.addTab(self.tab2, "Из файла")

        self.tab1.layout = QtWidgets.QVBoxLayout()
        self.grid_tab1 = QtWidgets.QGridLayout()

        self.btn_csu_connect = QtWidgets.QPushButton("Подключить")
        self.btn_csu_connect.setMaximumSize(120, 30)
        self.btn_csu_connect.setMinimumSize(120, 30)
        self.lbl_csu_connect = QtWidgets.QLabel("Источник тока")

        self.btn_vmu_connect = QtWidgets.QPushButton("Подключить")
        self.btn_vmu_connect.setMaximumSize(120, 30)
        self.btn_vmu_connect.setMinimumSize(120, 30)
        self.lbl_vmu_connect = QtWidgets.QLabel("Осциллограф")

        self.btn_run_measurement = QtWidgets.QPushButton("Запустить\n измерение")
        self.btn_run_measurement.setFont(QtGui.QFont('Arial', 12))
        self.btn_run_measurement.setMinimumSize(100, 50)
        self.btn_run_measurement.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.btn_save_result = QtWidgets.QPushButton("Сохранить\n результат")
        self.btn_save_result.setFont(QtGui.QFont('Arial', 12))
        self.btn_save_result.setMinimumSize(100, 50)
        self.btn_save_result.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_run_measurement = QtWidgets.QLabel("Измерения:")
        self.lbl_run_measurement.setFont(QtGui.QFont('Arial', 14))
        self.lbl_run_measurement.setMinimumSize(120, 30)
        self.lbl_run_measurement.setMaximumSize(120, 30)
        self.lbl_run_measurement.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_current_range = QtWidgets.QLabel("Рабочий диапазон:")
        self.cmb_current_range = QtWidgets.QComboBox(self)
        self.cmb_current_range.addItems(att_csu_ranges)

        self.lbl_start_current = QtWidgets.QLabel("Начальный ток, А:")
        self.led_start_current = QtWidgets.QLineEdit("0")
        self.led_start_current.setAlignment(QtCore.Qt.AlignCenter)
        self.led_start_current.setMaximumSize(120, 30)
        self.led_start_current.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_step_current = QtWidgets.QLabel("Шаг по току, А:")
        self.led_step_current = QtWidgets.QLineEdit("1e-9")
        self.led_step_current.setAlignment(QtCore.Qt.AlignCenter)
        self.led_step_current.setMaximumSize(120, 30)
        self.led_step_current.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_points_current = QtWidgets.QLabel("Количество точек:")
        self.led_points_current = QtWidgets.QLineEdit("101")
        self.led_points_current.setAlignment(QtCore.Qt.AlignCenter)
        self.led_points_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{5}")))
        self.led_points_current.setMaximumSize(120, 30)
        self.led_points_current.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_vmu_ch_current = QtWidgets.QLabel("Канал тока:")
        self.box_vmu_ch_current = QtWidgets.QComboBox(self)
        self.box_vmu_ch_current.addItems(['1', '2', '3', '4'])
        self.box_vmu_ch_current.setFont(QtGui.QFont('Arial', 12))
        self.box_vmu_flt_current = QtWidgets.QComboBox(self)
        self.box_vmu_flt_current.addItems(['Фильтр Выкл.', '20МГц', '200МГц'])
        self.box_vmu_flt_current.setFont(QtGui.QFont('Arial', 12))

        self.lbl_vmu_ch_voltage = QtWidgets.QLabel("Канал напряжения:")
        self.box_vmu_ch_voltage = QtWidgets.QComboBox(self)
        self.box_vmu_ch_voltage.addItems(['1', '2', '3', '4'])
        self.box_vmu_ch_voltage.setFont(QtGui.QFont('Arial', 12))
        self.box_vmu_flt_voltage = QtWidgets.QComboBox(self)
        self.box_vmu_flt_voltage.addItems(['Фильтр Выкл.', '20МГц', '200МГц'])
        self.box_vmu_flt_voltage.setFont(QtGui.QFont('Arial', 12))

        self.lbl_sampling_time = QtWidgets.QLabel("Шаг по времени, сек:")
        self.lbl_sampling_time.setFont(QtGui.QFont('Arial', 12))
        self.led_sampling_time = QtWidgets.QLineEdit("0.001")
        self.led_sampling_time.setAlignment(QtCore.Qt.AlignCenter)
        self.led_sampling_time.setMaximumSize(120, 30)
        self.led_sampling_time.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_measurement_mode = QtWidgets.QLabel("Режим измерения:")
        self.box_measurement_mode = QtWidgets.QComboBox(self)
        self.box_measurement_mode.addItems(['Стандартный', 'Оценивание'])
        self.box_measurement_mode.setFont(QtGui.QFont('Arial', 12))

        self.lbl_measurement_average = QtWidgets.QLabel('Усреднения:')
        self.led_measurement_average = QtWidgets.QLineEdit('1')
        self.led_measurement_average.setFont(QtGui.QFont('Arial', 12))
        self.led_measurement_average.setMinimumSize(120, 30)
        self.led_measurement_average.setAlignment(QtCore.Qt.AlignCenter)

        self.lbl_main_description = QtWidgets.QLabel("Измерение критического тока контакта")
        self.lbl_main_description.setFont(QtGui.QFont('Arial', 14))
        self.lbl_csu_params_label = QtWidgets.QLabel("Параметры источника тока:")
        self.lbl_csu_params_label.setFont(QtGui.QFont('Arial', 14))
        self.lbl_vmu_params_label = QtWidgets.QLabel("Параметры измерителя:")
        self.lbl_vmu_params_label.setFont(QtGui.QFont('Arial', 14))

        self.pbar = QtWidgets.QProgressBar(self)

        self.grid_tab1.addWidget(self.lbl_main_description, 0, 0, 1, 7)
        self.grid_tab1.addWidget(self.lbl_csu_connect, 1, 0, 1, 2)
        self.grid_tab1.addWidget(self.btn_csu_connect, 1, 2, 1, 2)
        self.grid_tab1.addWidget(self.lbl_vmu_connect, 1, 4, 1, 2, Qt.AlignLeft)
        self.grid_tab1.addWidget(self.btn_vmu_connect, 1, 6, 1, 2)

        self.grid_tab1.addWidget(self.lbl_csu_params_label, 2, 0, 1, 5)
        self.grid_tab1.addWidget(self.lbl_current_range, 3, 0, 1, 2, Qt.AlignLeft)
        self.grid_tab1.addWidget(self.cmb_current_range, 4, 0, 1, 2, Qt.AlignLeft)

        self.grid_tab1.addWidget(self.lbl_start_current, 5, 0, 1, 3)
        self.grid_tab1.addWidget(self.led_start_current, 6, 0, 1, 3)
        self.grid_tab1.addWidget(self.lbl_step_current,  5, 2, 1, 3)
        self.grid_tab1.addWidget(self.led_step_current,  6, 2, 1, 3)
        self.grid_tab1.addWidget(self.lbl_points_current, 5, 4, 1, 3)
        self.grid_tab1.addWidget(self.led_points_current, 6, 4, 1, 3)

        self.grid_tab1.addWidget(self.lbl_vmu_params_label, 7, 0, 1, 3)
        self.grid_tab1.addWidget(self.lbl_vmu_ch_current, 8, 0, 1, 2)
        self.grid_tab1.addWidget(self.box_vmu_ch_current, 9, 0, 1, 1)
        self.grid_tab1.addWidget(self.lbl_vmu_ch_voltage, 10, 0, 1, 2)
        self.grid_tab1.addWidget(self.box_vmu_ch_voltage, 11, 0, 1, 1)

        self.grid_tab1.addWidget(self.box_vmu_flt_current, 9, 1, 1, 1)
        self.grid_tab1.addWidget(self.box_vmu_flt_voltage, 11, 1, 1, 1)

        self.grid_tab1.addWidget(QtWidgets.QLabel(""), 12, 0, 3, 6)
        self.grid_tab1.addWidget(self.lbl_run_measurement, 13, 0, 1, 6)

        self.grid_tab1.addWidget(self.lbl_sampling_time, 14, 0, 1, 2)
        self.grid_tab1.addWidget(self.led_sampling_time, 15, 0, 1, 2)
        self.grid_tab1.addWidget(self.lbl_measurement_mode, 14, 3, 1, 2)
        self.grid_tab1.addWidget(self.box_measurement_mode, 15, 3, 1, 2)
        self.grid_tab1.addWidget(self.lbl_measurement_average, 14, 6, 1, 2)
        self.grid_tab1.addWidget(self.led_measurement_average, 15, 6, 1, 2)

        self.grid_tab1.addWidget(QtWidgets.QLabel(""), 16, 0, 3, 6)
        self.grid_tab1.addWidget(self.btn_run_measurement, 12+6, 0, 4, 2)
        self.grid_tab1.addWidget(self.btn_save_result, 12+6, 3, 4, 2)
        self.grid_tab1.addWidget(self.pbar, 22, 0, 1, 8)
        self.pbar.setValue(0)

        self.tab1.layout.insertLayout(0, self.grid_tab1)
        self.tab1.layout.addWidget(QtWidgets.QLabel(""), 1)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QtWidgets.QVBoxLayout()
        self.grid_tab2 = QtWidgets.QGridLayout()

        self.btn_load_file = QtWidgets.QPushButton("Загрузить данные\n из файла")
        self.btn_load_file.setMaximumSize(140, 60)
        self.btn_load_file.setMinimumSize(140, 60)
        self.btn_load_file.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.estimate_threshold_led = QtWidgets.QLineEdit("")
        self.estimate_threshold_led.setMaximumSize(120, 40)
        self.estimate_threshold_led.setMinimumSize(120, 40)
        self.estimate_threshold_led.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.table_of_params = QtWidgets.QTableWidget(self)
        self.table_of_params.setColumnCount(5)
        self.table_of_params.setMinimumSize(400, 200)
        self.table_of_params.setMaximumSize(2000, 2700)
        self.table_of_params.setRowCount(200)
        self.table_of_params.setHorizontalHeaderLabels(
            ["	I+-  ", "	I++  ", "V+-", "   V++	 ", "N+-"])
        self.table_of_params.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignCenter)
        self.table_of_params.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignCenter)
        self.table_of_params.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignCenter)
        self.table_of_params.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignCenter)
        self.table_of_params.horizontalHeaderItem(4).setTextAlignment(QtCore.Qt.AlignCenter)

        self.table_of_params.horizontalHeader().setStretchLastSection(True)

        self.table_of_params.resizeColumnsToContents()
        self.table_of_params.setColumnWidth(0, 120)
        self.table_of_params.setColumnWidth(1, 120)
        self.table_of_params.setColumnWidth(2, 120)
        self.table_of_params.setColumnWidth(3, 120)
        self.table_of_params.setColumnWidth(4, 120)

        self.estimate_value_led = QtWidgets.QLineEdit("")
        self.estimate_value_led.setMaximumSize(120, 40)
        self.estimate_value_led.setReadOnly(True)
        self.grid_tab2.addWidget(self.btn_load_file, 0, 0, 2, 3)
        # self.grid_tab2.addWidget(self.estimate_threshold_led, 3, 2, 2, 2)
        self.grid_tab2.addWidget(self.estimate_value_led, 3, 1, 2, 2)
        self.grid_tab2.addWidget(QtWidgets.QLabel("Оценка\nкритического тока:"), 3, 0, 2, 4)

        self.tab2.layout.insertLayout(0, self.grid_tab2)
        self.tab2.layout.addWidget(self.table_of_params, 1)
        self.tab2.setLayout(self.tab2.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ex = CommonWindow()
    ex.setFont(QtGui.QFont('Arial', 12))  # QtGui.QFont.Bold
    ex.setWindowTitle("Измерение и оценивание критического тока")
    ex.adjustSize()
    ex.show()
    sys.exit(app.exec_())  # run the cycle of processing the events
