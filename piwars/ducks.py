import os, sys
import math
import time

from . import robot

def approach1():
    left_power = right_power = 0.75
    power_increment = 0.1
    left_increment = right_increment = 0
    time_increment = 0.1

    t1 = time.time() + 10
    with robot.Robot() as robbie:
        while time.time() < t1:
            robbie.forwards(left_power + left_increment, right_power + right_increment)
            left_increment = right_increment = 0
            time.sleep(time_increment)
            robbie.stop()

            left_mm = robbie.get_left_mm()
            right_mm = robbie.get_right_mm()
            front_mm = robbie.get_front_mm()
            diff_mm = left_mm - right_mm
            print("Left: %4.2f; Right: %4.2f; Front: %4.2f; diff_mm %4.2f" % (left_mm, right_mm, front_mm, diff_mm))
            if front_mm < 400:
                break
            if diff_mm > -5:
                print("Moving left")
                right_increment = power_increment
            elif diff_mm < 5:
                print("Moving right")
                left_increment = power_increment

def approach2():
    left_power = right_power = 0.5
    power_increment = 0.025
    left_increment = right_increment = 0
    time_increment = 0.125
    diff_threshold = 5

    t1 = time.time() + 10
    sensor_time_threshold = 0
    with robot.Robot() as robbie:
        while time.time() < t1:
            robbie.forwards(left_power + left_increment, right_power + right_increment)
            left_increment = right_increment = 0
            time.sleep(time_increment)
            robbie.stop()

            if time.time() > sensor_time_threshold:
                right1_mm = robbie.get_front_mm()
                right2_mm = robbie.get_right_mm()
                diff_mm = right2_mm - right1_mm
                this_increment = power_increment * math.log(abs(diff_mm), 10)
                print("Back: %4.2f; Front: %4.2f; Diff_mm %4.2f" % (right1_mm, right2_mm, diff_mm))
                if diff_mm < -diff_threshold or right1_mm > 20 or right2_mm > 20:
                    print("Moving right")
                    left_increment = power_increment
                elif diff_mm > diff_threshold:
                    print("Moving left")
                    right_increment = power_increment

if __name__ == '__main__':
    approach1(*sys.argv[1:])
