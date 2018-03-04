#!/usr/bin/env python
# coding: Latin-1

# Simple example of a motor sequence script

# Import library functions we need
import ThunderBorg
import UltraBorg
import time
import sys

# Setup the ThunderBorg
global TB
TB = ThunderBorg.ThunderBorg()     # Create a new ThunderBorg object
#TB.i2cAddress = 0x15              # Uncomment and change the value if you have changed the board address
TB.Init()                          # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print 'No ThunderBorg found, check you are attached :)'
    else:
        print 'No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the IÂ²C address change the setup line so it is correct, e.g.'
        print 'TB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()

def get_right_sensor():
    return UB.GetDistance3()

def get_left_sensor():
    return UB.GetDistance4()

def get_front_sensor():
    return UB.GetDistance1()

def forward_left(power):
    TB.SetMotor1(power)

def backwards_left(power):
    TB.SetMotor1(-power)

def forward_right(power):
    TB.SetMotor2(power)

def backwards_right(power):
    TB.SetMotor2(-power)


# Setup the Ultraborg
UB = UltraBorg.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

stepDelay = 0.1                     # Number of seconds between each sequence step

while True:
    # Read all two ultrasonic values and convert to the nearest millimeter
    right_sensor_mm = get_right_sensor() # right sensor
    left_sensor_mm = get_left_sensor() # left sensor

    print "Left:", left_sensor_mm
    print "Right:", right_sensor_mm

    # Activate motor

    if left_sensor_mm < 1000 and right_sensor_mm < 1000:
        if left_sensor_mm > ((left_sensor_mm + right_sensor_mm)/2.0):
            print ("left_sensor_mm greater")
            backwards_left(0.2)
            backwards_right(0.5)
        elif right_sensor_mm > ((left_sensor_mm + right_sensor_mm)/2.0):
            print ("right_sensor_mm greater")
            backwards_left(0.5)
            backwards_right(0.2)
        else:
            print ("left_sensor_mm equals right_sensor_mm")
            backwards_left(0.5)
            backwards_right(0.5)
    else:
        if left_sensor_mm > ((left_sensor_mm + right_sensor_mm)/2.0):
            print ("left_sensor_mm greater dos")
            forward_left(0.3)
            backwards_right(0.3)
        elif right_sensor_mm > ((left_sensor_mm + right_sensor_mm)/2.0):
            print ("right_sensor_mm greater dos")
            backwards_left(0.3)
            forwards_right(0.3)
        else:
            print ("left_sensor_mm equals right_sensor_mm dos")
            backwards_left(0.5)
            backwards_right(0.5)

##        print '%+.1f %+.1f' % (step[0], step[1])
    time.sleep(stepDelay)                   # Wait between steps

