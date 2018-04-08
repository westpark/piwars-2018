"""
Log onto the Raspberry Pi as pi/t0adst00l
workon piwars # this sets up the Python virtualenv
cd work-in-progress/piwars-2018

python -mpiwars.ducks # this runs the module ducks in the piwars package

S1 - PAN: 5079/3888/1079
S2 - TILT: 2192/1408/969
S3 - BARREL: 4869/4869/969
S4 - TRIGGER:5303/5303/1246

"""
import os, sys
import time

from . import robot

shots =[-0.50, 0.60]
#shots =[-0.99, -0.45, 0.12, 0.80]
load =[0.95, 0.3,  -0.3, -0.95]

barrel_pos = 0

def rest_pose():
    save_trigger()
    time.sleep(0.5)
    base_pan.position = -1.0
    base_tilt.position = -0.2
    move_barrel(0)

def shoot():
    trigger.position = -1.0
    time.sleep(1.0)
    save_trigger()
    time.sleep(1.0)

def save_trigger():
    trigger.position = 1.0

def move_barrel(pos):
    if pos >= len(shots):
        return

    barrel_turn.position = shots[pos]
    time.sleep(1.0)

def load_barrel(pos):
    if pos >= len(shots):
        return

    barrel_turn.position = load[pos]
    time.sleep(1.0)

with robot.Robot() as robbie:
    base_pan = robbie.servos[3]
    base_tilt = robbie.servos[2]
    barrel_turn = robbie.servos[1]
    trigger = robbie.servos[0]

    print("min " + str( trigger.min))
    print("max "+ str( trigger.max))

    barrel_turn.min = 969
    trigger.startup = 5300
    #load_barrel(3)
    
    rest_pose()

    #shoot()
    #shoot()
    #move_barrel(0)
    #time.sleep(4)
    #move_barrel(2)
    
    #barrel_pos = 0
    #move_barrel(barrel_pos)
    for i in range(len(shots)):
        #pass
        move_barrel(i)
        #load_barrel(i)
        shoot()

    #shoot()
    #time.sleep(4)

    #shoot()

    #
    # .. or whatver
    #
    print("return barrel")
    barrel_turn.position = 0
    time.sleep(1)
    print("return everything else")


#    swivel_position = -1
#    for i in range(8):
#        base_swivel.position = swivel_position
#        swivel_position += 0.25
#        time.sleep(0.3)
