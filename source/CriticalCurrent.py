#!/usr/bin/python3
# -*- coding: utf-8 -*-
import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QWhatsThis
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QTimer


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
import threading
import selectors
import types
import drivers.ncs5
from system.matplotlibPyQt5 import MplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
__version__ = '1.0.0'
__author__ = 'lha_hl'


class CommonWindow(QtWidgets.QWidget): #QMainWindow QtWidgets.QWidget
	"""Класс основного окна программы"""
	def __init__(self, parent=None):
		#QtWidgets.QMainWindow.__init__(self, parent)

		super().__init__(parent)
		self.data_array = [0]*13
		self.data_bytearray = bytearray(self.data_array)

		vertical_size = 30
		horizontal_size = 80

		sc = MplCanvas(self, width=12, height=6, dpi=100)
		sc.plot_x_label = 'Counts'
		sc.plot_y_label = "Amplitude, a.u."
		sc.plot_title = 'Volt-Amp Characteristic JJ'
		sc.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
		toolbar = NavigationToolbar(sc, self)

		self.tab_wdg = Tabs(self, horizontal_size, vertical_size)

		self.vbox_level1 = QtWidgets.QVBoxLayout()
		self.vbox_level2 = QtWidgets.QVBoxLayout()
		self.hbox_level1 = QtWidgets.QHBoxLayout()
		self.hbox_level1.addWidget(self.tab_wdg)
		self.vbox_level2.addWidget(toolbar)
		self.vbox_level2.addWidget(sc)
		self.vbox_level2.addWidget((QtWidgets.QLabel("")), 2)

		self.hbox_level1.insertLayout(1, self.vbox_level2)
		# self.hbox_level1.addWidget(QtWidgets.QLabel(""),2)
		self.vbox_level1.insertLayout(0, self.hbox_level1)
		self.vbox_level1.addWidget(QtWidgets.QLabel(""))

		self.setLayout(self.vbox_level1)
		self.show()
		# self.setCentralWidget(sc)

	@staticmethod
	def load_from_file(path, file_type):
		try:
			if file_type == 'txt':
				print("load txt file")
			elif file_type == 'npy':
				print("load numpy file")
			else:
				print("unknown file type")
		except:
			traceback.print_exc()

	def save_result_to_file(self, path, data):
		print("save to file {}\\{}".format(path, data)) 


class Tabs(QtWidgets.QWidget):
	def __init__(self, parent, widget_width=80, widget_height=30):
		super(QtWidgets.QWidget, self).__init__(parent)
		super().__init__(parent)
		self.layout = QtWidgets.QVBoxLayout()
		self.__widget_width = widget_width
		self.__widget_height = widget_height

		self.tabs = QtWidgets.QTabWidget()
		self.tab1 = QtWidgets.QWidget()
		self.tab2 = QtWidgets.QWidget()
		self.tabs.setMinimumSize(400, 400)
		# self.tabs.setMaximumSize(400, 300)
		self.tabs.setMaximumWidth(500)
		self.tabs.resize(400, 400)

		self.tabs.addTab(self.tab1, "Measurement")
		self.tabs.addTab(self.tab2, "File")

		self.tab1.layout = QtWidgets.QVBoxLayout()
		self.grid_tab1 = QtWidgets.QGridLayout()

		self.btn_csu_connect = QtWidgets.QPushButton("Connect")
		self.lbl_csu_connect = QtWidgets.QLabel("CSU")
		
		self.btn_vmu_connect = QtWidgets.QPushButton("Connect")
		self.lbl_vmu_connect = QtWidgets.QLabel("VMU")

		self.btn_run_measurement = QtWidgets.QPushButton("Run")
		self.lbl_run_measurement = QtWidgets.QLabel("Measurement")

		self.lbl_current_range = QtWidgets.QLabel("Current range:")
		self.lbl_voltage_range = QtWidgets.QLabel("Voltage range")
		self.cmb_current_range = QtWidgets.QComboBox(self)
		self.cmb_current_range.addItems(['1uA', '10uA', '100uA', '1mA', '10mA', '50mA'])
		self.cmb_voltage_range = QtWidgets.QComboBox(self)
		self.cmb_voltage_range.addItems(['1nV', '1uV', '1mV', '1V'])

		self.lbl_start_current = QtWidgets.QLabel("Start current:")
		self.led_start_current = QtWidgets.QLineEdit("0")
		self.led_start_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))

		self.lbl_step_current = QtWidgets.QLabel("Step current:")
		self.led_step_current = QtWidgets.QLineEdit("0")
		self.led_step_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))

		self.lbl_points_current = QtWidgets.QLabel("Current points:")
		self.led_points_current = QtWidgets.QLineEdit("1")
		self.led_points_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))

		self.grid_tab1.addWidget(QtWidgets.QLabel("JJCC Measurements"), 0, 0, 1, 5)
		self.grid_tab1.addWidget(self.lbl_csu_connect, 1, 0, 1, 1)
		self.grid_tab1.addWidget(self.btn_csu_connect, 1, 1, 1, 1)
		self.grid_tab1.addWidget(self.lbl_vmu_connect, 1, 2, 1, 1, Qt.AlignCenter)
		self.grid_tab1.addWidget(self.btn_vmu_connect, 1, 3, 1, 1)
		self.grid_tab1.addWidget(self.lbl_current_range, 2, 0, 1, 1, Qt.AlignCenter)
		self.grid_tab1.addWidget(self.cmb_current_range, 2, 1, 1, 1, Qt.AlignCenter)
		self.grid_tab1.addWidget(self.lbl_voltage_range, 2, 2, 1, 1, Qt.AlignCenter)
		self.grid_tab1.addWidget(self.cmb_voltage_range, 2, 3, 1, 1, Qt.AlignCenter)
		self.grid_tab1.addWidget(QtWidgets.QLabel("Current source unit parameters:"), 3, 0, 1, 5)
		self.grid_tab1.addWidget(self.lbl_start_current, 4, 0, 1, 1)
		self.grid_tab1.addWidget(self.led_start_current, 4, 1, 1, 1)
		self.grid_tab1.addWidget(self.lbl_step_current,  4, 2, 1, 1)
		self.grid_tab1.addWidget(self.led_step_current,  4, 3, 1, 1)
		self.grid_tab1.addWidget(self.lbl_points_current, 4, 4, 1, 1)
		self.grid_tab1.addWidget(self.led_points_current, 4, 5, 1, 1)

		self.tab1.layout.insertLayout(0, self.grid_tab1)
		self.tab1.layout.addWidget(QtWidgets.QLabel(""), 1)
		self.tab1.setLayout(self.tab1.layout)

		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)


if __name__ == '__main__':
	import sys
	import time, math

	app = QtWidgets.QApplication(sys.argv)
	ex = CommonWindow()
	ex.setFont(QtGui.QFont('Arial', 9))  # QtGui.QFont.Bold
	ex.setWindowTitle("LQCE_Est v{}".format(__version__))
	ex.adjustSize()
	ex.show()
	sys.exit(app.exec_())  # run the cycle of processing the events
