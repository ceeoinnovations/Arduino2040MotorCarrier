import time
from motorController import *

board = NanoMotorBoard()
print("reboot")
board.reboot()
time.sleep_ms(500)

motors = []

# at 50 it works as expected, at 60 shift sides and is too small duty to move, at 70 is very big duty.
for i in range(2):
    motors.append(DCMotor(i))

for motor in motors:  # initialize
    b = motor.setDuty(0)

for duty in range(-100,100,1):
    print("Motor Duty: %d" % duty)
    for motor in motors:
        b = motor.setDuty(duty)
    time.sleep_ms(100)
 
for motor in motors:  # initialize
    b = motor.setDuty(0)
