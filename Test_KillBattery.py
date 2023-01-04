# pinout used https://www.amazon.com/Reduction-Multiple-Replacement-Velocity-Measurement/dp/B08DKJT2XF/ref=d_pd_di_sccai_cn_sccl_3_1/145-8390281-0998129?pd_rd_w=jYBFm&content-id=amzn1.sym.e13de93e-5518-4644-8e6b-4ee5f2e0b062&pf_rd_p=e13de93e-5518-4644-8e6b-4ee5f2e0b062&pf_rd_r=KX5BJF96QMEVHE275AZD&pd_rd_wg=ZcRhn&pd_rd_r=57bc5303-8936-46a0-8b6d-3e1e6bd180ff&pd_rd_i=B08DKJT2XF&psc=1

import time
from motorController import *

board = NanoMotorBoard()
def Init():
    print("reboot")
    board.reboot()
    time.sleep_ms(500)
    
    motors = []

    # at 50 it works as expected, at 60 shift sides and 
    #is too small duty to move, at 70 is very big duty.
    for i in range(2):
        motors.append(DCMotor(i))

    for motor in motors:  # initialize
        b = motor.setDuty(0)
        b = motor.resetEncoder(0)
    return motors

def Ramp(motors):
    for duty in range(-100,100,10):
        for motor in motors:
            print('Encoder: %d' % motor.readEncoder(),end=' ')
            b = motor.setDuty(duty)
        print('Duty: %d  Bat: %0.1f' % (duty, board.battery(0)))
        time.sleep_ms(100)

def Stop(motors):  
    for motor in motors:  # initialize
        b = motor.setDuty(0)

motors = Init()

good = True
start = time.time()
f = open('test.py','w')
f.write('')
f.close()
    
while good:
    for motor in motors:  # initialize
        b = motor.setDuty(0)
        b = motor.resetEncoder(0)
    Ramp(motors)
    Stop(motors)
    time.sleep(1)

    dt = time.time()-start
    string = '%d\t%d\t%d\t%0.1f\n'%(dt,motors[0].readEncoder(),motors[1].readEncoder(),board.battery(0))
    print(string)
    f = open('test.py','a')
    f.write(string)
    f.close()
    #if abs(motor.readEncoder()) < 5:
        #good = False
Stop(motors)
