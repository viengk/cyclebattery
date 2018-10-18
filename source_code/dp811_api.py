#!/usr/bin/env python
import visa

class PowerSupply(object):
    def __init__(self, identity=''):
        self.rm = visa.ResourceManager()
        self.device_list = self.rm.list_resources()
        print('Connected devices: ' + str(self.device_list))
        self.identity = identity
        if self.identity=='':
            self.identity = self.get_id()
        self.power_supply = self.rm.open_resource(self.identity)

    def get_id(self):
        for device_id in self.device_list:
            if (len(device_id.split('::')) == 5 and
                device_id.split('::')[3].startswith('DP')):
                print ('Power supply found: ' + device_id)
                return device_id    
        print ('Power supply not found.')
        return ''

    def write(self, command):
        self.power_supply.write(command)

    def query(self, command):
        return self.power_supply.query(command)

    def enable_sense(self):
        self.write(':OUTP:SENS ON')

    def read_voltage(self):
        return float(self.query(':MEAS:VOLT? CH1'))

    def read_current(self):
        return float(self.query(':MEAS:CURR? CH1'))

    def set_voltage_current(self, voltage, current):
        self.write(":APPL CH1,"+str(voltage)+','+str(current))

    def on(self):
        self.write(':OUTP CH1, ON')

    def off(self):
        self.write(':OUTP CH1, OFF')

ps = PowerSupply()
ps.set_voltage_current(3.68, 5.1)

