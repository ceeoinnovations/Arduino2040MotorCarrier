'''
This controls the Arduino Nano Motor COntroller board with the RP2040

ports etc - https://docs.arduino.cc/tutorials/nano-rp2040-connect/rp2040-python-api
translated from https://github.com/arduino-libraries/ArduinoMotorCarrier/blob/master/src/ArduinoMotorCarrier.cpp
'''

import time
import struct
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
    #print(payload)
    return i2c.writeto(I2C_ADDRESS, payload)

def version():
    return getData(GET_VERSION,4).decode()
        
def reboot():
    setData(RESET, 0, 0) 
    return True
    
def ping():
    return setData(PING, 0, 0) > 0
    
def temperature():
    data = getData(GET_INTERNAL_TEMP,4)
    t = float(struct.unpack('i',data)[0])
    return t / 1000.0

def getIrqStatus():
    data = getData(CLEAR_IRQ, 4)
    return struct.unpack('i',data)[0]

def RAM():
    data = getData(GET_FREE_RAM, 4)
    return struct.unpack('i',data)[0]
    
def battery(mode=0): # 0 - raw, 1-converted, 2-filtered
    cmds = [GET_RAW_ADC_BATTERY,GET_CONVERTED_ADC_BATTERY,GET_FILTERED_ADC_BATTERY]
    data = getData(cmds[mode], 4)
    n = struct.unpack('i',data)[0]
    return n if mode else n/236
    
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

class DCMotor():
    '''
    motor0 = DCMotor(0,50) means first motor instance and pwm frequency of 50Hz
    '''
    def __init__(self, instance = 0, frequency = 50):
        self.instance = instance
        self.setFrequency(frequency)
        
    def setDuty(self, duty):
        return setData(SET_PWM_DUTY_CYCLE_DC_MOTOR, self.instance, duty);
    
    def setFrequency(self, frequency):
        return setData(SET_PWM_FREQUENCY_DC_MOTOR, self.instance, frequency);
        
#Encoder
    def resetEncoder(self, value = 0):
        return setData(RESET_COUNT_ENCODER, self.instance, value)
        
    def readEncoder(self):
        data = getData(GET_RAW_COUNT_ENCODER, 4, self.instance)
        return  struct.unpack('i',data)[0]
        
    def getOverflowUnderflow(self):
        r = getData(GET_OVERFLOW_UNDERFLOW_STATUS_ENCODER, 2, self.instance)
        return r[0] << 8 | r[1]
    
    def getCountPerSecond(self):
        data = getData(GET_COUNT_PER_SECOND_ENCODER, 4, self.instance)
        return  struct.unpack('i',data)[0]
            
    def setIrqOnCount(self, value):
        return setData(SET_INTERRUPT_ON_COUNT_ENCODER, self.instance, value)
        
    def setIrqOnVelocity(self, value, margin = 2):
        return setData(SET_INTERRUPT_ON_VELOCITY_ENCODER, self.instance, (margin << 24 | value));
    
#PID    
    def setControlMode(self, mode): 
        # mode: 0 - open loop, 1- position, 2 - vvelocity
        return setData(SET_CONTROL_MODE_CL_MOTOR, self.instance, mode);
        
    def setGains(self, kp, ki, kd):
        payload = struct.pack('fff',kp,ki,kd)
        return setData(SET_PID_GAIN_CL_MOTOR,self.instance,payload)
        
    def getGains(self):
        reply = getData(GET_PID_VAL, 4*3, self.instance)
        return struct.unpack('fff',reply)
        
    def resetGains(self):
        return setData(RESET_PID_GAIN_CL_MOTOR, self.instance, 0)

    def setMaxAcceleration(self, maxAccel):
        return setData(SET_MAX_ACCELERATION_CL_MOTOR, self.instance, maxAccel)
            
    def setMaxVelocity(self, maxVelocity):
        return setData(SET_MAX_VELOCITY_CL_MOTOR, self.instance, maxVelocity)
        
    def setLimits(self, minDuty, maxDuty):
        return setData(SET_MIN_MAX_DUTY_CYCLE_CL_MOTOR, self,instance, (minDuty << 16 | maxDuty))
        
    def setSetpoint(self, mode, target): 
        # mode: 0 - velocity target, 1 - position
        if (mode == TARGET_POSITION):
            setData(SET_POSITION_SETPOINT_CL_MOTOR, self.instance, target)
        if (mode == TARGET_VELOCITY):
            if not target:
                setData(SET_PWM_DUTY_CYCLE_DC_MOTOR, self.instance, target) # Fix target = 0 issue in PID_VELOCITY mode.
            else:
                setData(SET_VELOCITY_SETPOINT_CL_MOTOR, self.instance, target)
                
class Servo():
    '''
    servo1 = Servo(1) means it is the first servo instance you are controlling
    '''
    def __init__(self, instance):
        self.instance = instance
        
    def setAngle(self, angle):
        angle =  int(7 + (angle/180 * (28 - 7)))
        return setData(SET_PWM_DUTY_CYCLE_SERVO, self.instance, angle)
    
    def detach(self):
        return setData(SET_PWM_DUTY_CYCLE_SERVO, self.instance, -1)
    
    def setFrequency(self, frequency):
        return setData(SET_PWM_FREQUENCY_SERVO, self.instance, frequency)
                    
fred = DCMotor(0) 
fred.setDuty(0)

fred.resetGains()
fred.setGains(1000,200,1)
fred.getGains()

fred.setControlMode(CL_POSITION)
target = 1000
fred.setSetpoint(TARGET_POSITION, target)

bill = Servo(1)
bill.setFrequency(50)
bill.setAngle(90)

