#!/usr/bin/env python
import time
import datetime
import configparser
import atexit
from dl3031_api import ElectronicLoad

TRUE_STRINGS = ['true', 'yes', 'y', 't', 'yep', 'yup', 'certainly', 'x', '1']
FIRST_DATA_LINE = 'Time, Voltage, Current, Power'

def set_up_electronic_load():
        electronic_load.set_cutoff_voltage(DISCHARGE_CUTOFF_VOLTAGE)
        electronic_load.set_discharge_current(DISCHARGE_CURRENT)
        electronic_load.enable_sense()
        electronic_load.set_mode(RANG)
        electronic_load.set_mode(MODE)
        electronic_load.set_alevel(ALEVEL)
        electronic_load.set_blevel(BLEVEL)
        electronic_load.set_period(PERIOD)
        electronic_load.set_aduty(ADUTY)

def get_setting(setting):
    if config[config_profile][setting]:
        return config[config_profile][setting]
    return config['DEFAULT'][setting]

def time_string():
    return datetime.datetime.now().strftime(FILENAME_TIME_FORMAT)

def get_data_line():
    return (str(datetime.datetime.now())+','
            + str(electronic_load.read_voltage())+','
            + str(electronic_load.read_current())+','
            + str(electronic_load.read_power())+'\n')
            #+ str(electronic_load.read_capacity())+','
            #+ str(electronic_load.read_watthours())+'\n')
            #+ str(electronic_load.read_discharge_time())+'\n')

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

def full_discharge(csvfile):
    electronic_load.on()
    time.sleep(1) #wait for load to turn on
    while electronic_load.read_voltage() > DISCHARGE_CUTOFF_VOLTAGE:
        record_data(csvfile, electronic_load)
    electronic_load.off()
    print ("Discharge done at: " + str(datetime.datetime.now()))

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
    n = input('\nEnter the corresponding number between 0 and '+str(len(keys)-1)+': ')
    return keys[int(n)]

def shutdown():
    electronic_load.off()

def discharge(cycle_number):
    with open('data\\' + DISCHARGE_FILENAME + "_" + str(cycle_number - 1) + "_" + time_string() + '.csv', 'w') as csvfile:
        csvfile.write(FIRST_DATA_LINE+',Cycle profile used:,'+config_profile+'\n')
        if USE_TIMED_CYCLE.lower() in TRUE_STRINGS:
            print('Timed discharge')
            timed_discharge(csvfile)
        else:
            full_discharge(csvfile)
    time.sleep(DISCHARGE_COMPLETE_WAIT_TIME)
    global num_lines
    num_lines += DISCHARGE_COMPLETE_WAIT_TIME / RECORD_TIME_INTERVAL

electronic_load = ElectronicLoad()
electronic_load.write('*CLR')
time.sleep(2)
shutdown()
#atexit.register(shutdown)

config = configparser.ConfigParser()
config.read('config.ini')
config_profile = choose_setting() #waiting for operator input

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
RANG = get_setting('RANG')
MODE = get_setting('MODE')
ALEVEL = float(get_setting('ALEVEL'))
BLEVEL = float(get_setting('BLEVEL'))
PERIOD = float(get_setting('PERIOD'))
ADUTY = float(get_setting('ADUTY'))

set_up_electronic_load()
time.sleep(5)

start_time = 0
num_lines = 0
cycle_number = 1

electronic_load.on()
time.sleep(2)
#electronic_load.tran_on()
#time.sleep(10)
electronic_load.write(':SYST:KEY 42') #waveform display key
time.sleep(2)
#electronic_load.write(':SYST:KEY 19') #sixth menu key - next
#time.sleep(2)
#electronic_load.write(':SYST:KEY 15') #second menu key - record
#time.sleep(2)
electronic_load.tran_on()
time.sleep(2)
#vbatt = electronic_load.read_voltage()
with open('data\\' + DISCHARGE_FILENAME + "_" + time_string() + '.csv', 'w') as csvfile:
    csvfile.write(FIRST_DATA_LINE+',Cycle profile used:,'+config_profile+'\n')

    #max = 6
    #start = time.time()
    while electronic_load.read_voltage() > DISCHARGE_CUTOFF_VOLTAGE:
        time.sleep(2)
        #vbatt = electronic_load.read_voltage()
        #record_data(csvfile, electronic_load)
        data_line = get_data_line()
        csvfile.write(data_line)
    
        #remaining = max + start - time.time()
    
        #if remaining <= 0:
            #start = time.time()
            #electronic_load.tran_on()

#electronic_load.write(':SYST:KEY 15') #second menu key - record
#time.sleep(5)

electronic_load.tran_off()
electronic_load.off()
time.sleep(2)
electronic_load.write('*CLR')
time.sleep(2)
#print ("Done")
print ("Discharge done at: " + str(datetime.datetime.now()))

