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

def approach3():
    """Track the left hand side and *reduce* power (so we can run at full)

    * Track the left-hand side, not the difference
    * To turn right, reduce the right power so we can usually run at full

    EXPERIENCE: the trouble with this approach is that if the robot starts
    to slew -- and it does! -- then the left distance will not get smaller even
    though the robot is turning into the left side. That said, the right side
    will increase.
    """
    side_threshold_mm = 150
    left_power = right_power = 0.75
    power_increment = 0.1
    left_increment = right_increment = 0
    time_increment = 0.1

    t1 = time.time() + 10
    with robot.Robot() as robbie:
        while time.time() < t1:
            robbie.forwards(left_power + left_increment, right_power + right_increment)
            time.sleep(time_increment)

            left_mm = robbie.get_left_mm()
            right_mm = robbie.get_right_mm()
            front_mm = robbie.get_front_mm()
            print("Left: %4.2f; Right: %4.2f; Front: %4.2f" % (left_mm, right_mm, front_mm))
            if front_mm < 400:
                break
            if left_mm < side_threshold_mm:
                print("About to move right")
                left_increment = +power_increment
                right_increment = -power_increment
            elif right_mm < side_threshold_mm:
                print("About to move left")
                right_increment = +power_increment
                left_increment = -power_increment
            else:
                left_increment = right_increment = 0

def approach4():
    """Track the left hand side and *reduce* power (so we can run at full)

    * Track the differential of the left-hand side, not the left-right difference
    * To turn right, reduce the right power so we can usually run at full
    """
    dleft_threshold_mm = dright_threshold_mm = 3 ## if we've moved by this much, go the other way
    base_power = 1
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
            time.sleep(time_increment)

            left_mm = robbie.get_left_mm()
            right_mm = robbie.get_right_mm()
            front_mm = robbie.get_front_mm()
            print("Left: %4.2f; Right: %4.2f; Front: %4.2f" % (left_mm, right_mm, front_mm))
            if front_mm < 400:
                break
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

if __name__ == '__main__':
    approach4(*sys.argv[1:])
