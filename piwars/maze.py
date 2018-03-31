import os, sys
import time

from . import robot

with robot.Robot() as robbie:
    robbie.forwards()
    for i in range (100) :
        time.sleep(0.5)
        print(robbie.get_front_mm())
        if (robbie.get_front_mm())<130:
             robbie.stop()
             break

    robbie.turn_right(1,1.5)
    robbie.forwards()
    time.sleep(10)