import os, sys
import time
import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()

from . import robot

#
# On PS3 controller:
#
# Left joystick
# - Axis 0 - horizontal
# - Axis 1 - vertical
# Right joystick
# - Axis 2 - horizontal
# - Axis 3 - vertical
# Left button set:
# - LRUD - 7,5,4,6
# - (also registers as axes)
# Right button set:
# - LRUD - 15,13,12,14
# - (also registers as axes)
# Top buttons:
# - Left - Upper 10, Lower 8
# - Right - Upper 11, Lower 9
# (joystick, also has accelerometer which registers as axes)
# [Select] - button 0
# [Start] - button 3
#

# Settings for the joystick
axisUpDown = 1                          # Joystick axis to read for up / down position
axisLeftRight = 2                       # Joystick axis to read for left / right position
buttonSlow = 8                          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 9                      # Joystick button number for turning fast (R2)
buttonStop = 13
interval = 0.00                         # Time between updates in seconds, smaller responds faster but uses more processor time

def initialise_joystick():
    print("Waiting for joystick...")
    pygame.joystick.init()
    while pygame.joystick.get_count() < 1:
        time.sleep(0.1)
    joystick = pygame.joystick.Joystick(0)
    print("Found", joystick.get_name())
    joystick.init()
    return joystick

def handle_axis_move(event, speeds):
    left, right = speeds
    if event.axis == axisUpDown:
        left = right = -event.value

    elif event.axis == axisLeftRight:
        movement = event.value
        if abs(movement) > 0.1:
            if movement < 0:
                left = -right * abs(movement)
            elif movement > 0:
                right = -left * abs(movement)
            else:
                left = right = max(left, right)

    return left, right

def handle_button_down(event, speeds):
    return speeds

def remote_control(robbie):
    joystick = initialise_joystick()
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0

    old_speeds = speeds = 0, 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == buttonStop:
                return
            if event.type == pygame.JOYAXISMOTION and event.axis in (axisUpDown, axisLeftRight):
                speeds = handle_axis_move(event, speeds)
            elif event.type == pygame.JOYBUTTONDOWN and event.button in (buttonSlow, buttonFastTurn):
                speeds = handle_button_down(event, speeds)

            if speeds != old_speeds:
                left, right = speeds
                robbie.go(left, right)
                old_speeds = speeds

        time.sleep(interval)

if __name__ == '__main__':
    with robot.Robot() as robbie:
        remote_control(robbie)

