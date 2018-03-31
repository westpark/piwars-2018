import os, sys
import time

from . import robot
from . import joystick

class Remote(object):

    def __init__(self, robbie, controller):
        self.robbie = robbie
        self.controller = controller

        self.speeds = 0, 0
        self.running = True
        self.controller.handle_left_axis_h = self.handle_axis_move
        self.controller.handle_left_axis_v = self.handle_axis_move
        self.controller.handle_right_quadrant_w = self.stop

    def handle_axis_move(self, event):
        left, right = self.speeds
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

        self.speeds = left, right

    def stop(self):
        self.running = False

    def start(self):
        upDown = 0.0
        leftRight = 0.0

        old_speeds = self.speeds = 0, 0
        while self.running:
            self.controller.run_once()
            if self.speeds != old_speeds:
                left, right = self.speeds
                robbie.go(left, right)
                old_speeds = self.speeds
            time.sleep(interval)

if __name__ == '__main__':
    with robot.Robot() as robbie:
        controller = joystick.Joystick()
        remote = Remote(robbie, controller)
        remote.start()
