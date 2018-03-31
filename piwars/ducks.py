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

shots =[-0.9, -0.3, 0.25, 0.95]
load =[0.95, 0.3,  -0.3, -0.95]

def rest_pose():
    base_pan.position = -1.0
    base_tilt.position = -0.2
    move_barrel(0)
    trigger.position = 1.0
    time.sleep(1.0)

def shoot():
    trigger.position = -1.0
    time.sleep(0.5)
    trigger.position = 1.0
    time.sleep(0.5)

def move_barrel(pos):
    if pos >= len(shots):
        return

    barrel_turn.position = shots[pos]
    time.sleep(2.0)

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

    
    #load_barrel(3)
    #move_barrel(3)

    #shoot()
    rest_pose()
    #move_barrel(2)
    
    
    for i in range(len(shots)):
        #pass
        move_barrel(i)
        #load_barrel(i)
        shoot()

    #shoot()

    #
    # .. or whatver
    #

#    swivel_position = -1
#    for i in range(8):
#        base_swivel.position = swivel_position
#        swivel_position += 0.25
#        time.sleep(0.3)
