import os, sys
import math
import time

from . import robot

def maze():
    """Track the left hand side and *reduce* power (so we can run at full)

    * Track the differential of the left-hand side, not the left-right difference
    * To turn right, reduce the right power so we can usually run at full
    """
    dleft_threshold_mm = dright_threshold_mm = 3 ## if we've moved by this much, go the other way
    base_power = .5
    power_increment = base_power * 0.2
    left_power = right_power = base_power
    left_increment = right_increment = 0
    time_increment = 0.1

    t1 = time.time() + 10
    with robot.Robot() as robbie:
        previous_left_mm = left_mm = robbie.get_left_mm()
        previous_right_mm = right_mm = robbie.get_right_mm()
        while time.time() < t1:
            robbie.forwards(left_power + left_increment, right_power + right_increment)
            front_mm = robbie.get_front_mm()
            print("Left: %4.2f; Right: %4.2f; Front: %4.2f" % (left_mm, right_mm, front_mm))
            if front_mm < 400:
                return
            left_mm = robbie.get_left_mm()
            right_mm = robbie.get_right_mm()
            dleft_mm = previous_left_mm - left_mm
            dright_mm = previous_right_mm - right_mm
            if dleft_mm > dleft_threshold_mm:
                print("Moved left by %smm; About to move right" % dleft_mm)
                left_increment = +power_increment
                right_increment = -power_increment
            #
            # Better to let it be guided from the left; otherwise
            # there's a lot of jinking
            #
            #~ elif dright_mm > dright_threshold_mm:
                #~ print("About to move left")
                #~ right_increment = +power_increment
                #~ left_increment = -power_increment
            else:
                left_increment = right_increment = 0
            previous_left_mm = left_mm
            previous_right_mm = right_mm
            time.sleep(time_increment)


def start_stop():
    with robot.Robot() as robbie:
        print("Battery:", robbie.battery_level)
        robbie.forwards(.5, .5)
        print()
        print("Battery:", robbie.battery_level)
        time.sleep(0.5)
        robbie.stop()
        print()
        print("Front:", robbie.get_front_mm())
        print("Front Raw:", robbie.get_front_mm(use_raw=True))
        print("Battery:", robbie.battery_level)
        time.sleep(1)
        print()
        print("Front:", robbie.get_front_mm())
        print("Front Raw:", robbie.get_front_mm(use_raw=True))
        print("Battery:", robbie.battery_level)
        time.sleep(5)
        print()
        print("Front:", robbie.get_front_mm())
        print("Front Raw:", robbie.get_front_mm(use_raw=True))
        print("Battery:", robbie.battery_level)


if __name__ == '__main__':
    start_stop(*sys.argv[1:])
