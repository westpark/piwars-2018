import os, sys
import time
import pygame

from . import robot

# Settings for the joystick
axisUpDown = 1                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 2                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
buttonSlow = 8                          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 9                      # Joystick button number for turning fast (R2)
interval = 0.00                         # Time between updates in seconds, smaller responds faster but uses more processor time

# Power settings
voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
voltageOut = 6.0                       # Maximum motor voltage
maxPower = max(voltageOut / voltageIn, 1.0)

os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()

def initialise_joystick():
    print('Waiting for joystick... (press CTRL+C to abort)')
    while True:
        try:
            try:
                pygame.joystick.init()
                # Attempt to setup the joystick
                if pygame.joystick.get_count() < 1:
                    # No joystick attached, set LEDs blue
                    pygame.joystick.quit()
                    time.sleep(0.1)
                else:
                    # We have a joystick, attempt to initialise it!
                    joystick = pygame.joystick.Joystick(0)
                    break
            except pygame.error:
                # Failed to connect to the joystick, set LEDs blue
                pygame.joystick.quit()
                time.sleep(0.1)
        except KeyboardInterrupt:
            # CTRL+C exit, give up
            print('\nUser aborted')
            sys.exit()
    
    print('Joystick found')
    joystick.init()
    return joystick

def remote_control(robbie):
    joystick = initialise_joystick()
    try:
        print('Press CTRL+C to quit')
        driveLeft = 0.0
        driveRight = 0.0
        running = True
        hadEvent = False
        upDown = 0.0
        leftRight = 0.0
        # Loop indefinitely
        while running:
            # Get the latest events from the system
            hadEvent = False
            events = pygame.event.get()
            # Handle each event individually
            for event in events:
                if event.type == pygame.QUIT:
                    # User exit
                    running = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    # A button on the joystick just got pushed down
                    hadEvent = True
                elif event.type == pygame.JOYAXISMOTION:
                    # A joystick has been moved
                    hadEvent = True
                if hadEvent:
                    
                    # Read axis positions (-1 to +1)
                    if axisUpDownInverted:
                        upDown = -joystick.get_axis(axisUpDown)
                    else:
                        upDown = joystick.get_axis(axisUpDown)
                    if axisLeftRightInverted:
                        leftRight = -joystick.get_axis(axisLeftRight)
                    else:
                        leftRight = joystick.get_axis(axisLeftRight)
                    
                    # Apply steering speeds
                    if not joystick.get_button(buttonFastTurn):
                        leftRight *= 0.5
                    # Determine the drive power levels
                    driveLeft = -upDown
                    driveRight = -upDown
                    if leftRight < -0.05:
                        # Turning left
                        driveLeft *= 1.0 + (2.0 * leftRight)
                    elif leftRight > 0.05:
                        # Turning right
                        driveRight *= 1.0 - (2.0 * leftRight)
                    # Check for button presses
                    if joystick.get_button(buttonSlow):
                        driveLeft *= slowFactor
                        driveRight *= slowFactor
                    # Set the motors to the new speeds
                    robbie.go(driveLeft * maxPower * 100.0, driveRight * maxPower * 100.0)
            # Change LEDs to purple to show motor faults
            #~ if TB.GetDriveFault1() or TB.GetDriveFault2():
                #~ if ledBatteryMode:
                    #~ TB.SetLedShowBattery(False)
                    #~ TB.SetLeds(1,0,1)
                    #~ ledBatteryMode = False
            #~ else:
                #~ if not ledBatteryMode:
                    #~ TB.SetLedShowBattery(True)
                    #~ ledBatteryMode = True
            # Wait for the interval period
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")

if __name__ == '__main__':
    with robot.Robot() as robbie:
        remote_control(robbie)

