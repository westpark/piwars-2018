import os, sys
import logging
import time

from . import robot
from . import joystick

logger = logging.getLogger("piwars.remote")
logger.addHandler(logging.StreamHandler())

class Remote(object):

    def __init__(self, robbie, controller):
        self.robbie = robbie
        self.controller = controller

        self.speeds = 0, 0
        self.running = True
        self.controller.handle_left_stick_v = self.handle_axis_up_down
        self.controller.handle_right_stick_h = self.handle_axis_left_right
        self.controller.handle_right_quadrant_e = self.stop

    def handle_axis_up_down(self, event):
        self.speeds = (-event.value, -event.value)

    def handle_axis_left_right(self, event):
        left, right = self.speeds
        movement = event.value
        if abs(movement) > 0.1:
            if movement < 0:
                left = -right * abs(movement)
            elif movement > 0:
                right = -left * abs(movement)
            else:
                left = right = max(left, right)
        self.speeds = left, right

    def stop(self, _):
        self.running = False

    def start(self):
        interval = 0.1

        old_speeds = self.speeds = 0, 0
        while self.running:
            self.controller.run_once()
            if self.speeds != old_speeds:
                left, right = self.speeds
                robbie.go(left, right)
                old_speeds = self.speeds
            time.sleep(interval)

if __name__ == '__main__':
    logging.getLogger("piwars.joystick").setLevel(logging.DEBUG)
    logging.getLogger("piwars.remote").setLevel(logging.DEBUG)
    with robot.Robot() as robbie:
        controller = joystick.Joystick()
        remote = Remote(robbie, controller)
        remote.start()
