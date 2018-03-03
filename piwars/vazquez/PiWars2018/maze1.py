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

# Loop over the sequence until the user presses CTRL+C
print 'Press CTRL+C to finish'
try:
    while True:
        # Read all two ultrasonic values and convert to the nearest millimeter
        try:
            usm1 = int (UB.GetDistance3()) # right sensor
            usm2 = int (UB.GetDistance4()) # left sensor
        except:
            print ("reading error")
      
        # Display the readings
        if usm1 == 0:
            print '#1 (right) No reading'
        else:
            print '#1 (right) % 4d mm' % (usm1)
        if usm2 == 0:
            print '#2 (left) No reading'
        else:
            print '#2 (left) % 4d mm' % (usm2)

        # Activate motor        

        if usm1 < 1000 and usm2 < 1000:
            if usm1 > ((usm1 + usm2)/2.0):
                print ("usm1 greater")
                TB.SetMotor1(-0.2)
                TB.SetMotor2(-0.5)
            elif usm2 > ((usm1 + usm2)/2.0):
                print ("usm2 greater")
                TB.SetMotor1(-0.5)
                TB.SetMotor2(-0.2)
            else:
                print ("usm1 equals usm2")
                TB.SetMotor1(-0.5)
                TB.SetMotor2(-0.5)
        else:
            if usm1 > ((usm1 + usm2)/2.0):
                print ("usm1 greater dos")
                TB.SetMotor1(0.3)
                TB.SetMotor2(-0.3)
            elif usm2 > ((usm1 + usm2)/2.0):
                print ("usm2 greater dos")
                TB.SetMotor1(-0.3)
                TB.SetMotor2(0.3)
            else:
                print ("usm1 equals usm2 dos")
                TB.SetMotor1(-0.5)
                TB.SetMotor2(-0.5)
        
##        print '%+.1f %+.1f' % (step[0], step[1])
        time.sleep(stepDelay)                   # Wait between steps
        
except KeyboardInterrupt:
    # User has pressed CTRL+C
    TB.MotorsOff()                 # Turn both motors off
    print 'Done'
finally:
    TB.MotorsOff()
    
