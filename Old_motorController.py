# ports etc - https://docs.arduino.cc/tutorials/nano-rp2040-connect/rp2040-python-api
# translated from https://github.com/arduino-libraries/ArduinoMotorCarrier/blob/master/src/ArduinoMotorCarrier.cpp

import time
from machine import I2C, Pin
from MC_Consts import *

i2c = I2C(0, sda=Pin(12),scl=Pin(13),freq=400000)  
I2C_ADDRESS in i2c.scan()

def getData(cmd = 0x01, replylength = 0, target = 0x00):
    b = i2c.writeto(I2C_ADDRESS, bytearray([cmd,target])) 
    if replylength <= 0:
        return None
    replylength += 1  # add for status byte
    reply = i2c.readfrom(I2C_ADDRESS, replylength) 
    if not reply:
        print('failed')
        return None
    if reply[0] != 0:
        print('controller.irq_status = status')
        return ord(reply[0])
    return reply[1:]

def setData(cmd, target, data):
    if (type(data) == type(bytes())):
         payload = bytes([cmd,target]) + data
    else:
        payload = bytes([cmd,target]) + data.to_bytes(4, 'little')
    return i2c.writeto(I2C_ADDRESS, payload)

def version():
    return getData(GET_VERSION,4).decode()
        
def reboot():
    getData(RESET, 0, 0) 
    return True
    
def ping():
    return len(getData(PING, 1))>0
    
def temperature():
    t = float(getData(GET_INTERNAL_TEMP,2))
    return t / 1000.0

def getIrqStatus():
    r = getData(CLEAR_IRQ, 1)
    return ord(r)

def RAM():
    r = getData(GET_FREE_RAM, 1)
    return ord(r)
    
def battery(mode=0): # 0 - raw, 1-converted, 2-filtered
    cmds = [GET_RAW_ADC_BATTERY,GET_CONVERTED_ADC_BATTERY,GET_FILTERED_ADC_BATTERY]
    data = getData(cmds[mode], 4)
    n = int.from_bytes(data, byteorder='little', signed=False)
    return n/236 
    
def enable_battery_charging():
    # Only if the board is a nano 33 IoT
    
    # min sys voltage 3.88 V + max input current 2.0 A
    b = i2c.writeto(PMIC_ADDRESS, bytearray([PMIC_REG00,0x06]))
    # Charge Battery + Minimum System Voltage 3.5 V
    b = i2c.writeto(PMIC_ADDRESS, bytearray([PMIC_REG01,0x1B]))
    # Charge current  512 mA
    b = i2c.writeto(PMIC_ADDRESS, bytearray([PMIC_REG02,0x00]))
    # Charge Voltage Limit 4.128 V
    b = i2c.writeto(PMIC_ADDRESS, bytearray([PMIC_REG04,0x9E]))
    # Enable Battery Charge termination + disable watchdog
    b = i2c.writeto(PMIC_ADDRESS, bytearray([PMIC_REG05,0x8A]))

ping()
version()
getIrqStatus()
#temperature()
RAM()
#enable_battery_charging()

