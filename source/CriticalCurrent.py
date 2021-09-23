#!/usr/bin/python3
# -*- coding: utf-8 -*-

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


__version__ = '1.0.0'
__author__ = 'lha_hl'


class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)

		self.data_array = [0]*13
		self.data_bytearray = bytearray(self.data_array)

		vertical_size = 30
		horizontal_size = 80

		self.tab_wdg = tabsWidget(self, horizontal_size, vertical_size)

		self.hbox_level1 = QtWidgets.QHBoxLayout()
		self.hbox_level1.addWidget(self.tab_wdg)
		self.hbox_level1.addWidget(QtWidgets.QLabel(""))

		self.setLayout(self.hbox_level1)

	@staticmethod
	def load_from_file(self, path, file_type):
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

class tabsWidget(QtWidgets.QWidget):
	def __init__(self, parent, widget_width = 80, widget_height = 30):
		super(QtWidgets.QWidget, self).__init__(parent)
		self.layout = QtWidgets.QVBoxLayout()
		self.__widget_width = widget_width
		self.__widget_height = widget_height

		self.tabs = QtWidgets.QTabWidget()
		self.tab1 = QtWidgets.QWidget() # server tab
		self.tab2 = QtWidgets.QWidget() # client tab
		self.tabs.setMinimumSize(350, 280)
		self.tabs.resize(350, 280)

		self.tabs.addTab(self.tab1, "From File")
		self.tabs.addTab(self.tab2, "Measurement")

		self.tab1.layout = QtWidgets.QVBoxLayout()
		self.grid_tab1 = QtWidgets.QGridLayout()

		self.btn_csu_connect = QtWidgets.QPushButton("Connect")
		self.lbl_csu_connect = QtWidgets.QLabel("CSU")
		
		self.btn_vmu_connect = QtWidgets.QPushButton("Connect")
		self.lbl_vmu_connect = QtWidgets.QLabel("VMU")

		self.btn_run_measurement = QtWidgets.QPushButton("Run")
		self.lbl_run_measurement = QtWidgets.QLabel("Measurement")

		self.lbl_start_current = QtWidgets.QLabel("Start current:")
		self.led_start_current = QtWidgets.QLineEdit("0")
		self.led_start_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))

		self.lbl_step_current = QtWidgets.QLabel("Step current:")
		self.led_step_current = QtWidgets.QLineEdit("0")
		self.led_step_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))

		self.lbl_points_current = QtWidgets.QLabel("Current points:")
		self.led_points_current = QtWidgets.QLineEdit("1")
		self.led_points_current.setValidator(QRegExpValidator(QtCore.QRegExp("[0-9]{4}|[a-fA-F0-9]{4}")))

		self.grid_tab1.addWidget(QtWidgets.QLabel("JJCC Measurements"), 0,0, 5, 1)
		self.grid_tab1.addWidget(self.lbl_csu_connect, 0, 1, 1, 1)
		self.grid_tab1.addWidget(self.btn_csu_connect, 1, 1, 1, 1)
		self.grid_tab1.addWidget(QtWidgets.QLabel("Current source unit parameters:"), 0, 2, 5, 1)
		self.grid_tab1.addWidget(self.lbl_start_current, 0,3,1,1)
		self.grid_tab1.addWidget(self.led_start_current, 1,3,1,1)
		self.grid_tab1.addWidget(self.lbl_step_current,  2,3,1,1)
		self.grid_tab1.addWidget(self.led_step_current,  3,3,1,1)
		self.grid_tab1.addWidget(self.lbl_points_current, 4,3,1,1)
		self.grid_tab1.addWidget(self.led_points_current, 5,3,1,1)

		self.tab1.layout.insertLayout(0, self.grid_tab1)
		self.tab1.layout.addWidget(QtWidgets.QLabel(""), 1)
		self.tab1.setLayout(self.tab1.layout)

		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)


if __name__ == '__main__':
	import sys
	import time, math

	app =QtWidgets.QApplication(sys.argv)
	ex = CommonWindow()
	ex.setFont(QtGui.QFont('Arial', 9))  # QtGui.QFont.Bold
	ex.setWindowTitle("LQCE_Est v{}".format(__version__))
	# ex.adjustSize()
	ex.show()
	sys.exit(app.exec_()) # run the cycle of processing the events
