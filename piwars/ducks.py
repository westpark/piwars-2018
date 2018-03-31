"""
Log onto the Raspberry Pi as pi/t0adst00l
workon piwars # this sets up the Python virtualenv
cd work-in-progress/piwars-2018

python -mpiwars.ducks # this runs the module ducks in the piwars package
"""
import os, sys
import time

from . import robot

with robot.Robot() as robbie:
    base_swivel = robbie.servos[3]
    gun_tilt = robbie.servos[2]
    barrel_turn = robbie.servos[1]
    #
    # .. or whatver
    #

    swivel_position = -1
    for i in range(8):
        base_swivel.position = swivel_position
        swivel_position += 0.25
        time.sleep(0.3)
