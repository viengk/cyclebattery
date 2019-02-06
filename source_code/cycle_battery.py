#!/usr/bin/env python
import time
import datetime
import configparser
import atexit
from dp811_api import PowerSupply
from dl3031_api import ElectronicLoad

TRUE_STRINGS = ['true', 'yes', 'y', 't', 'yep', 'yup', 'certainly', 'x', '1']
FIRST_DATA_LINE = 'Time,Power Supply Voltage,Power Supply Current,Electronic Load Voltage, Electronic Load Current'
def set_up_power_supply():
    power_supply.set_voltage_current(CHARGE_VOLTAGE, CHARGE_CURRENT)
    power_supply.enable_sense()
    
def set_up_electronic_load():
    electronic_load.set_cutoff_voltage(DISCHARGE_CUTOFF_VOLTAGE)
    electronic_load.set_discharge_current(DISCHARGE_CURRENT)
    electronic_load.enable_sense()

def get_setting(setting):
    if config[config_profile][setting]:
        return config[config_profile][setting]
    return config['DEFAULT'][setting]

def time_string():
    return datetime.datetime.now().strftime(FILENAME_TIME_FORMAT) 

def get_data_line():
    return (str(datetime.datetime.now())+','
            + str(power_supply.read_voltage())+','
            + str(power_supply.read_current())+','
            + str(electronic_load.read_voltage())+','
            + str(electronic_load.read_current())+'\n')
   
def wait():
    global start_time
    global num_lines
    if start_time == 0:
        start_time = time.time()
    num_lines = num_lines + 1
    sleep_time = (start_time + num_lines * RECORD_TIME_INTERVAL) - time.time()
    if sleep_time > 0:
        time.sleep(sleep_time)
    
def record_data(csvfile, insturment_object):
    wait()
    data_line = get_data_line()
    csvfile.write(data_line)
    print (type(insturment_object).__name__ + ': ' + data_line)

def full_charge(csvfile):
    power_supply.on()
    time.sleep(2) # Current takes a few seconds to stabalize
    while power_supply.read_current() > CHARGE_CUTOFF_CURRENT:
        record_data(csvfile, power_supply)
    top_off_charge(csvfile)
    power_supply.off()
    print ("Charging done at: " + str(datetime.datetime.now()))
    
def top_off_charge(csvfile):
    end_time = time.time() + TOP_OFF_CHARGE_TIME
    while time.time() < end_time:
        record_data(csvfile, power_supply)

def full_discharge(csvfile):
    electronic_load.on()
    time.sleep(1) #wait for load to turn on
    while electronic_load.read_voltage() > DISCHARGE_CUTOFF_VOLTAGE:
        record_data(csvfile, electronic_load)
    electronic_load.off()
    print ("Discharge done at: " + str(datetime.datetime.now()))

def timed_charge(csvfile):
    power_supply.on()
    time.sleep(2) # Current takes a few seconds to stabalize
    end_time = TIMED_CHARGE_TIME + time.time()
    while time.time() < end_time:
        record_data(csvfile, power_supply)
    power_supply.off()
    print ("Timed charging done at: " + str(datetime.datetime.now()))
    
def timed_discharge(csvfile):
    electronic_load.on()
    time.sleep(1) # Wait for load to turn on
    end_time = TIMED_DISCHARGE_TIME + time.time()
    while time.time() < end_time:
        record_data(csvfile, electronic_load)
    electronic_load.off()
    print ("Timed discharging done at: " + str(datetime.datetime.now()))
    
def choose_setting():
    print('\n'*60 + 'Choose which battery cycling profile you want to run.\n')
    keys = list(config.keys())
    for setting in keys:
        print (str(keys.index(setting))+': '+setting)
    n = input('\nEnter the corrisponding number between 0 and '+str(len(keys)-1)+': ')
    return keys[int(n)]

def shutdown():
    electronic_load.off()
    power_supply.off()

def charge():
    with open('data\\' + CHARGE_FILENAME + time_string() + '.csv', 'w') as csvfile:
        csvfile.write(FIRST_DATA_LINE+',Cycle profile used:,'+config_profile+'\n')
        if USE_TIMED_CYCLE.lower() in TRUE_STRINGS:
            print('Timed charge')
            timed_charge(csvfile)
        else:
            full_charge(csvfile)
    time.sleep(CHARGE_COMPLETE_WAIT_TIME)

def discharge():
    with open('data\\' + DISCHARGE_FILENAME + time_string() + '.csv', 'w') as csvfile:
        csvfile.write(FIRST_DATA_LINE+',Cycle profile used:,'+config_profile+'\n')
        if USE_TIMED_CYCLE.lower() in TRUE_STRINGS:
            print('Timed charge')
            timed_discharge(csvfile)
        else:
            full_discharge(csvfile)
    time.sleep(DISCHARGE_COMPLETE_WAIT_TIME)
    
            
power_supply = PowerSupply()
electronic_load = ElectronicLoad()
shutdown()
atexit.register(shutdown)

config = configparser.ConfigParser()
config.read('config.ini')
config_profile = choose_setting()

CHARGE_FIRST = get_setting('CHARGE_FIRST')
CHARGE_VOLTAGE = float(get_setting('CHARGE_VOLTAGE'))
CHARGE_CURRENT = float(get_setting('CHARGE_CURRENT'))
CHARGE_CUTOFF_CURRENT = float(get_setting('CHARGE_CUTOFF_CURRENT'))
TOP_OFF_CHARGE_TIME = float(get_setting('TOP_OFF_CHARGE_TIME'))
DISCHARGE_CURRENT = float(get_setting('DISCHARGE_CURRENT'))
DISCHARGE_CUTOFF_VOLTAGE = float(get_setting('DISCHARGE_CUTOFF_VOLTAGE'))
CHARGE_FILENAME = get_setting('CHARGE_FILENAME')
DISCHARGE_FILENAME = get_setting('DISCHARGE_FILENAME')
FILENAME_TIME_FORMAT = get_setting('FILENAME_TIME_FORMAT')
RECORD_TIME_INTERVAL = float(get_setting('RECORD_TIME_INTERVAL'))
USE_TIMED_CYCLE = get_setting('USE_TIMED_CYCLE')
CHARGE_FIRST = get_setting('CHARGE_FIRST')
TIMED_CHARGE_TIME = float(get_setting('TIMED_CHARGE_TIME'))
TIMED_DISCHARGE_TIME = float(get_setting('TIMED_DISCHARGE_TIME'))
CHARGE_COMPLETE_WAIT_TIME = float(get_setting('CHARGE_COMPLETE_WAIT_TIME'))
DISCHARGE_COMPLETE_WAIT_TIME = float(get_setting('DISCHARGE_COMPLETE_WAIT_TIME'))
NUMBER_CHARGES = int(get_setting('NUMBER_CHARGES'))

set_up_power_supply()
set_up_electronic_load()

start_time = 0
num_lines = 0
cycle_number = 1

if CHARGE_FIRST.lower() in TRUE_STRINGS:
    while True and NUMBER_CHARGES != cycle_number:
        cycle_number += 1
        charge()
        discharge()
else:
    while True and NUMBER_CHARGES != cycle_number:
        cycle_number += 1
        discharge()
        charge()


