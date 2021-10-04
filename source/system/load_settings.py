import numpy as np
import sys
from configparser import ConfigParser
import pathlib


class LoadSettings:

    def __init__(self):
        self.data = list()
        self.filepath = 'settings.ini'
        self.config = ConfigParser()
        self.font_size = 9
        self.csu_device = ''
        self.csu_connection_type = ''
        self.csu_ip = ''
        self.csu_port = 0
        self.vmu_device = ''
        self.vmu_connection_type = ''
        self.vmu_ip = ''
        self.vmu_serial_address = 1

    def open_file(self, filepath: str = '{}\\settings.ini'.format(pathlib.Path(__file__).parent.resolve())):
        self.config.read(filepath)

    def processing_file_data(self):
        self.font_size = self.config.get('system', 'font_size')
        print('[system] font size: {}'.format(self.font_size))
        self.csu_device = self.config.get('csu_config', 'device')
        print('[csu_config] device: {}'.format(self.csu_device))
        self.csu_connection_type = self.config.get('csu_config', 'connection_type')
        print('[csu_config] connection_type: {}'.format(self.csu_connection_type))
        self.csu_ip = self.config.get('csu_config', 'ip_address')
        print('[csu_config] ip_address: {}'.format(self.csu_ip))
        self.csu_port = self.config.getint('csu_config', 'port')
        print('[csu_config] port: {}'.format(self.csu_port))
        self.vmu_device = self.config.get('vmu_config', 'device')
        print('[vmu_config] device: {}'.format(self.vmu_device))
        self.vmu_connection_type = self.config.get('vmu_config', 'connection_type')
        print('[vmu_config] connection_type: {}'.format(self.vmu_connection_type))
        self.vmu_ip = self.config.get('vmu_config', 'ip_address')
        print('[vmu_config] ip_address: {}'.format(self.vmu_ip))
        self.vmu_serial_address = self.config.getint('vmu_config', 'serial_address')
        print('[vmu_config] serial_address: {}'.format(self.vmu_serial_address))

