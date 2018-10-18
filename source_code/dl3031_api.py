#!/usr/bin/env python
import visa

class ElectronicLoad(object):
    def __init__(self, identity=''):
        self.rm = visa.ResourceManager()
        self.device_list = self.rm.list_resources()
        print('Connected devices: ' + str(self.device_list))
        self.identity = identity
        if self.identity=='':
            self.identity = self.get_id()
        self.electronic_load = self.rm.open_resource(self.identity)

    def get_id(self):
        for device_id in self.device_list:
            if (len(device_id.split('::')) == 5 and
                device_id.split('::')[3].startswith('DL')):
                print ('Electronic load found: ' + device_id)
                return device_id    
        print ('Electronic load not found.')
        return ''

    def write(self, command):
        self.electronic_load.write(command)

    def query(self, command):
        return self.electronic_load.query(command)

    def enable_sense(self):
        self.write(':SOUR:SENS ON')

    def read_voltage(self):
        return float(self.query(':MEAS:VOLT?'))

    def read_current(self):
        return float(self.query(':MEAS:CURR?'))

    def set_cutoff_voltage(self, voltage):
        self.write(":SOUR:CURR:VON "+str(voltage))

    def set_discharge_current(self, current):
        self.write(":SOUR:CURR:LEV:IMM "+str(current))

    def on(self):
        self.write(':SOUR:INP:STAT ON')

    def off(self):
        self.write(':SOUR:INP:STAT OFF')
