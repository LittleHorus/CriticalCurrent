# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 13:37:39 2019

@author: Dmitry
"""
import re
import visa
from pyvisa.resources import MessageBasedResource

#Lecroy use VICP protocol for communication


class Lecroy:
    
    def __init__(self, visa_name):
        self.visa_name = visa_name
        self.rm = visa.ResourceManager()
        self._visainstrument = self.rm.open_resource(self.visa_name, resource_pyclass=MessageBasedResource)
        
        # self.cls()
        # self._visainstrument.read_termination = '\n'
        self._visainstrument.expect_termination = False
        self._visainstrument.timeout = 10000
        self.bandwidth_limit = "OFF"  # FULL
        self.timebase = 10e-6
        self.trig_couple = "DC1M"  # DC 1MOhm
        self.trig_level = 1  # 1 Volt
    
    def read(self):
        return self._visainstrument.read()

    def query(self, command):
        return self._visainstrument.query(command)

    def write(self, command):
        self._visainstrument.write(command)

    def set_timeout(self, timeout):
        self._visainstrument.timeout = timeout

    def read_bytes(self, counts):
        return self._visainstrument.read_bytes(counts)
    
    def get_id(self):
        return self.query("*IDN?")

    def arm(self):
        self.write("ARM")

    def clear(self):
        self.write("CLSW")

    def read_raw(self):
        return self._visainstrument.read_raw()    
    
    def stop_acquisition(self):
        self.write("STOP")
    
    def set_comm_header_format(self, header_format):
        # OFF SHORT LONG
        self.write("COMM_HEADER {}".format(header_format))
    
    def set_timebase_division(self, time_division):
        self.timebase = time_division*10
        self.write("TDIV {}".format(time_division))

    def get_timebase_division(self):
        tstring = self.query("TDIV?")
        tsub = tstring.split('TDIV ')
        t = tsub[1].split(' S\n')
        return float(t[0])
    
    def set_msize(self, samples):
        self.write("MSIZ {}".format(samples))

    def get_msize(self):
        mstring = self.query("MSIZ?")
        msub = mstring.split('MSIZ ')
        m = msub[1].split(' SAMPLE\n')
        return int(float(m[0]))

    def set_trigger_delay(self, delay_value):
        self.trigger_delay = delay_value
        self.write("TRDL {}".format(delay_value))

    def get_trigger_delay(self):
        return self.query("TRDL?")

    def set_trigger_coupling(self, coupling):
        self.trigger_coupling = coupling
        self.write("TRCP {}".format(coupling))

    def get_trigger_coupling(self):
        return self.query("TRCP?")

    def set_trigger_level(self, tlevel):
        self.trigger_level = tlevel
        self.write("TRLV {}".format(tlevel))

    def get_trigger_level(self):
        tstring = self.query("TRLV?")
        tsub = tstring.split('EX:TRLV ')
        t = tsub[1].split(' V')
        return float(t[0])

    def set_trigger_mode(self, mode):
        # NORM AUTO SINGLE STOP
        self.write("TRMD {}".format(mode))

    def get_trigger_mode(self):
        return self.query("TRMD?")

    def set_trigger_slope(self, slope):
        # POS NEG
        self.write("TRSL {}".format(slope))

    def get_trigger_slope(self):
        return self.query("TRSL?")

    def set_trigger_type(self, trigger_type):        
        self.write("TRSE {}, SR, EX, HT, OFF".format(trigger_type))

    def get_trigger_type(self):
        tstring = self.query("TRSE?")
        tsub = tstring.split('TRSE ')
        t = tsub[1].split(',')
        return t[0]

    def set_channel_coupling(self, channel, coupling):
        # D1M D50 A1M GND
        if 0 < channel < 5:
            self.write("C{}:CPL {}".format(channel, coupling))
        else:
            print("incorrect channel number")

    def get_channel_coupling(self, channel):
        if 0 < channel < 5:
            return self.query("C{}:CPL?".format(channel))
        else:
            print("incorrect channel number")

    def set_channel_vert_division(self, channel, vertical_division):
        if 0 < channel < 5:
            self.write("C{}:VDIV {}".format(channel, vertical_division))
        else:
            print("incorrect channel value")

    def get_channel_vert_division(self, channel):
        if 0 < channel < 5:
            vstring = self.query("C{}:VDIV?".format(channel))
            vsub = vstring.split('C{}:VDIV '.format(channel))
            v = vsub[1].split(' V\n')
            return float(v[0])
        else:
            print("incorrect channel number")

    def set_vert_offset(self, channel, offset):
        if 0 < channel < 5:
            self.write("C{}:OFST {}".format(channel, offset))
        else:
            print("incorrect channel number")

    def get_vert_offset(self, channel):
        if 0 < channel < 5:
            return self.query("C{}:OFST?".format(channel))
        else:
            print("incorrect channel number")

    def set_bandwidth_limit(self, channel, bw):
        if 0 < channel < 5:
            bw_prep = 'OFF'
            if type(bw) is int or type(bw) is float:
                if bw <= 20e6:
                    bw_prep = 'ON'
                elif 20e6 < bw <= 200e6:
                    bw_prep = '200MHz'
                elif bw > 200e6:
                    bw_prep = 'OFF'
                else:
                    bw_prep = 'OFF'
            if type(bw) is str:
                bw_prep = bw
            self.write("BWL C{}, {}".format(channel, bw_prep))
        else:
            print("incorrect channel number")

    def get_bandwidth_limit(self, channel): 
        qstring = self.query("BWL?")
        pstring = re.split(r'\W+', qstring)
        qlist = []
        for i in range(4):
            qlist.append(pstring[2*i+2])
        if 0 < channel < 5:
            return qlist[channel-1]
        else:
            print("incorrect channel number")
    
    def set_channel_state(self, channel, state):
        if 0 < channel < 5:
            self.write("C{}:TRA {}".format(channel, state))
        else:
            print("incorrect channel number")

    def get_channel_state(self, channel):
        if 0 < channel < 5:
            cstring = self.query("C{}:TRA?".format(channel))
            csub = cstring.split('C{}:TRA '.format(channel))
            return csub[1].split('\n')
        else:
            print("incorrect channel number")

    def get_waveform(self, channel, bytes_count):
        self.write("C{}:WF? DAT1".format(channel))
        bdata = self.read_bytes(bytes_count)
        header_off_data = bdata[16:]
        energy = 0
        temp = []
        for i in range(int(len(header_off_data)/2)):
            sd = header_off_data[2*i:2*i+2]
            temp.append(int.from_bytes(sd, byteorder='little', signed=True))
            energy += temp[i]**2
        return temp, energy

    def set_comm_format(self, cformat):
        # BYTE or WORD param
        self.write("CFMT DEF9, {}, BIN".format(cformat))
        # COMM_FORMAT DEF9, WORD, BIN

    def get_comm_format(self):
        return self.query("COMM_FORMAT?")
        
    def set_byte_order(self, order):
        self.write("CORD {}".format(order))
    