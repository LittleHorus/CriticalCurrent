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
from system.modeling import Model
import matplotlib.pyplot as plt
__version__ = '1.0.0'
__author__ = 'lha_hl'


class CommonWindow(QtWidgets.QWidget):  # QMainWindow QtWidgets.QWidget
    """Класс основного окна программы"""
    def __init__(self, parent=None):
        # QtWidgets.QMainWindow.__init__(self, parent)

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

        meas = Measurement(self.open_settings.csu_device, self.open_settings.vmu_device)
        att_csu_ranges = meas.csu_ranges

        vertical_size = 30
        horizontal_size = 80

        self.table_previous_row = 0
        self.table_current_row = 0

        self.sc = MplCanvas(self, width=12, height=6, dpi=100)
        self.sc.plot_x_label = 'Counts'
        self.sc.plot_y_label = "Amplitude, a.u."
        self.sc.plot_title = 'Volt-Amp Characteristic JJ'
        toolbar = NavigationToolbar(self.sc, self)
        self.sc.setMinimumWidth(700)

        self.tab_wdg = Tabs(self, horizontal_size, vertical_size, att_csu_ranges)

        self.vbox_level1 = QtWidgets.QVBoxLayout()
        self.vbox_level2 = QtWidgets.QVBoxLayout()
        self.hbox_level1 = QtWidgets.QHBoxLayout()
        self.hbox_level1.addWidget(self.tab_wdg)
        self.vbox_level2.addWidget(toolbar)
        self.vbox_level2.addWidget(self.sc)
        self.vbox_level2.addWidget((QtWidgets.QLabel("")), 2)

        self.hbox_level1.insertLayout(1, self.vbox_level2)
        # self.hbox_level1.addWidget(QtWidgets.QLabel(""),2)
        self.vbox_level1.insertLayout(0, self.hbox_level1)
        self.vbox_level1.addWidget(QtWidgets.QLabel(""))

        self.setLayout(self.vbox_level1)
        self.show()
        self.tab_wdg.btn_csu_connect.clicked.connect(self.on_connect_csu)
        self.tab_wdg.btn_vmu_connect.clicked.connect(self.on_connect_vmu)
        self.tab_wdg.btn_load_file.clicked.connect(self.on_load_from_file)

        average_count = 100
        self.current_em = list()
        self.voltage_em = list()
        for i in range(average_count):
            self.current_em.append(Model.current_emul(1e-7, 100, 10e-8))
            self.voltage_em.append(Model.contact_emul(self.current_em[i], 2e-6, 1))
        tupple_data = Estimation.estimate_cc(self.current_em, self.voltage_em, 1e-7, 1.0)

        est_current = tupple_data[0]
        table_ipm = tupple_data[1]
        table_ipp = tupple_data[2]
        table_vpm = tupple_data[3]
        table_vpp = tupple_data[4]
        table_i = tupple_data[5]
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
        self.sc.plot(self.current_em[0], self.voltage_em[0])
        self.sc.plot(self.current_em[1], self.voltage_em[1])

        self.tab_wdg.table_of_params.itemClicked.connect(self.on_change_active_row)

    def on_change_active_row(self):
        self.table_previous_row = self.table_current_row
        self.table_current_row = self.tab_wdg.table_of_params.currentRow()
        print('current row: {} {}'.format(self.table_current_row, self.table_previous_row))
        try:
            self.tab_wdg.table_of_params.selectRow(self.table_current_row)
            if self.table_current_row < len(self.current_em):
                self.sc.plot(self.current_em[self.table_current_row], self.voltage_em[self.table_current_row])

        except Exception as exc:
            print("Exception: {}".format(exc))

    def on_load_from_file(self):
        file_type = 'prn'
        filename = ''
        result_data = list()
        result_current = list()
        result_voltage = list()
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open file', self.common_path,
                "Text files(*.txt);;Numpy(*.npy);;Mathcad(*prn)", "Mathcad (*.prn)")[0]
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
            else:
                raise Exception('UnknownDataTypeError')
        except Exception as exc:
            print(exc)
        print(result_data)
        return result_data

    @staticmethod
    def save_result_to_file(path, data):
        print("save to file {}\\{}".format(path, data))

    def on_connect_csu(self):
        try:
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
        self.tabs.setMinimumSize(500, 500)
        # self.tabs.setMaximumSize(400, 300)
        self.tabs.setMaximumWidth(700)
        self.tabs.resize(500, 500)

        self.tabs.addTab(self.tab1, "Measurement")
        self.tabs.addTab(self.tab2, "File")

        self.tab1.layout = QtWidgets.QVBoxLayout()
        self.grid_tab1 = QtWidgets.QGridLayout()

        self.btn_csu_connect = QtWidgets.QPushButton("Connect")
        self.lbl_csu_connect = QtWidgets.QLabel("CSU")

        self.btn_vmu_connect = QtWidgets.QPushButton("Connect")
        self.lbl_vmu_connect = QtWidgets.QLabel("VMU")

        self.btn_run_measurement = QtWidgets.QPushButton("Run")
        self.btn_run_measurement.setMinimumSize(100, 50)
        self.btn_run_measurement.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.lbl_run_measurement = QtWidgets.QLabel("Measurement")
        self.lbl_run_measurement.setFont(QtGui.QFont('Arial', 12))
        self.lbl_run_measurement.setMinimumSize(120, 30)
        self.lbl_run_measurement.setMaximumSize(120, 30)
        self.lbl_run_measurement.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_current_range = QtWidgets.QLabel("Current range:")
        self.lbl_voltage_range = QtWidgets.QLabel("Voltage range:")
        self.cmb_current_range = QtWidgets.QComboBox(self)
        self.cmb_current_range.addItems(att_csu_ranges)
        self.cmb_voltage_range = QtWidgets.QComboBox(self)
        self.cmb_voltage_range.addItems(att_vmu_ranges)

        self.lbl_start_current = QtWidgets.QLabel("Start current:")
        self.led_start_current = QtWidgets.QLineEdit("0")
        self.led_start_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))
        self.led_start_current.setMaximumSize(120, 30)
        self.led_start_current.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_step_current = QtWidgets.QLabel("Step current:")
        self.led_step_current = QtWidgets.QLineEdit("0")
        self.led_step_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))
        self.led_step_current.setMaximumSize(120, 30)
        self.led_step_current.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_points_current = QtWidgets.QLabel("Current points:")
        self.led_points_current = QtWidgets.QLineEdit("1")
        self.led_points_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))
        self.led_points_current.setMaximumSize(120, 30)
        self.led_points_current.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lbl_main_description = QtWidgets.QLabel("JJCC Measurements")
        self.lbl_main_description.setFont(QtGui.QFont('Arial', 12))

        self.grid_tab1.addWidget(self.lbl_main_description, 0, 0, 1, 5)
        self.grid_tab1.addWidget(self.lbl_csu_connect, 1, 0, 1, 1)
        self.grid_tab1.addWidget(self.btn_csu_connect, 1, 1, 1, 1)
        self.grid_tab1.addWidget(self.lbl_vmu_connect, 1, 2, 1, 1, Qt.AlignCenter)
        self.grid_tab1.addWidget(self.btn_vmu_connect, 1, 3, 1, 1)
        self.grid_tab1.addWidget(self.lbl_current_range, 2, 0, 1, 2, Qt.AlignLeft)
        self.grid_tab1.addWidget(self.cmb_current_range, 3, 0, 1, 2, Qt.AlignLeft)
        self.grid_tab1.addWidget(self.lbl_voltage_range, 2, 2, 1, 2, Qt.AlignLeft)
        self.grid_tab1.addWidget(self.cmb_voltage_range, 3, 2, 1, 2, Qt.AlignLeft)
        self.grid_tab1.addWidget(QtWidgets.QLabel("Current source unit parameters:"), 4, 0, 1, 5)
        self.grid_tab1.addWidget(self.lbl_start_current, 5, 0, 1, 3)
        self.grid_tab1.addWidget(self.led_start_current, 6, 0, 1, 3)
        self.grid_tab1.addWidget(self.lbl_step_current,  5, 2, 1, 3)
        self.grid_tab1.addWidget(self.led_step_current,  6, 2, 1, 3)
        self.grid_tab1.addWidget(self.lbl_points_current, 5, 4, 1, 3)
        self.grid_tab1.addWidget(self.led_points_current, 6, 4, 1, 3)

        self.grid_tab1.addWidget(QtWidgets.QLabel(""), 7, 0, 3, 6)
        self.grid_tab1.addWidget(self.lbl_run_measurement, 10, 0, 2, 6)
        self.grid_tab1.addWidget(self.btn_run_measurement, 12, 0, 4, 2)
        # self.grid_tab1.addWidget(QtWidgets.QLabel("test"), 12, 2, 1, 1)

        self.tab1.layout.insertLayout(0, self.grid_tab1)
        self.tab1.layout.addWidget(QtWidgets.QLabel(""), 1)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QtWidgets.QVBoxLayout()
        self.grid_tab2 = QtWidgets.QGridLayout()

        self.btn_load_file = QtWidgets.QPushButton("Load \n from file")
        self.btn_load_file.setMaximumSize(120, 60)
        self.btn_load_file.setMinimumSize(120, 60)
        self.btn_load_file.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

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
        self.grid_tab2.addWidget(self.estimate_value_led, 3, 2, 2, 2)
        self.grid_tab2.addWidget(QtWidgets.QLabel("Critical Current\n Estimation:"), 3, 0, 2, 4)

        self.tab2.layout.insertLayout(0, self.grid_tab2)
        self.tab2.layout.addWidget(self.table_of_params, 1)
        self.tab2.setLayout(self.tab2.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ex = CommonWindow()
    ex.setFont(QtGui.QFont('Arial', 10))  # QtGui.QFont.Bold
    ex.setWindowTitle("LQCE_Est v{}".format(__version__))
    ex.adjustSize()
    ex.show()
    sys.exit(app.exec_())  # run the cycle of processing the events
