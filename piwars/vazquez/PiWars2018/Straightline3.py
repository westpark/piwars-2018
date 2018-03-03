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
    
# Setup the Ultraborg
UB = UltraBorg.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

stepDelay = 0.1                     # Number of seconds between each sequence step

"""
corridorwidth = 534
sensorswidth = 195
idealdistancetowall = (corridorwidth - sensorswidth)/2
print idealdistancetowall
"""

try:
    right_sensor = int (UB.GetDistance1())
    left_sensor = int (UB.GetDistance3())
except:
    print ("error en las lecturas")
    # Display the readings

if right_sensor == 0:
    print 'right_sensor No reading'
else:
    print 'right_sensor % 4d mm' % (right_sensor)

if left_sensor == 0:
    print 'left_sensor No reading'
else:
    print 'left_sensor % 4d mm' % (left_sensor)

# Loop over the sequence until the user presses CTRL+C
print 'Press CTRL+C to finish'
try:
    while True:
        # Read all two ultrasonic values and convert to the nearest millimeter
        try:
            right_sensor = int (UB.GetDistance2())
            left_sensor = int (UB.GetDistance4())
        except:
            print ("error en las lecturas")
      
        # Display the readings
        if right_sensor == 0:
            print 'right_sensor No reading'
        else:
            print 'right_sensor % 4d mm' % (right_sensor)
        if left_sensor == 0:
            print 'left_sensor No reading'
        else:
            print 'left_sensor % 4d mm' % (left_sensor)
 
        # Activate motor

        distance_both = float (right_sensor + left_sensor)
        print 'distance_both % 4d mm' % (distance_both)

        left_desviation= float (float (right_sensor)/distance_both)
        print 'left_desviation'
        print left_desviation

        if left_desviation > 0.0 and left_desviation < 0.33:
            print ("left_desviation > 0.0 and left_desviation < 0.33")
            TB.SetMotor1(-0.5)
            TB.SetMotor2(-0.4)
        elif left_desviation > 0.33 and left_desviation < 0.66:
            print ("left_desviation > 0.33 and left_desviation < 0.66")
            TB.SetMotor1(-0.4)
            TB.SetMotor2(-0.4)
        elif left_desviation > 0.66 and left_desviation < 1:
            print ("left_desviation > 0.66 and left_desviation < 1")
            TB.SetMotor1(-0.4)
            TB.SetMotor2(-0.5)
        else:
            print ("otro intervalo para left_desviation")
            TB.SetMotor1(-0.4)
            TB.SetMotor2(-0.4)
        
        time.sleep(stepDelay)                   # Wait between steps
        
except KeyboardInterrupt:
    # User has pressed CTRL+C
    TB.MotorsOff()                 # Turn both motors off
    print 'Done'
finally:
    TB.MotorsOff()
