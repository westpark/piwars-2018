import os, sys
import logging
import threading
import time

#
# Create a logger without any handlers.
#
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()

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

class Joystick(object):

    stick_handlers = {
        0 : "left_stick_h",
        1 : "left_stick_v",

        2 : "right_stick_h",
        3 : "right_stick_v",
    }
    button_handlers = {
        4 : "left_buttons_n",
        5 : "left_buttons_e",
        6 : "left_buttons_s",
        7 : "left_buttons_w",

        12 : "right_buttons_n",
        13 : "right_buttons_e",
        14 : "right_buttons_s",
        15 : "right_buttons_w",
    }

    def __init__(self):
        logger.debug("Waiting for joystick...")
        pygame.joystick.init()
        while pygame.joystick.get_count() < 1:
            time.sleep(0.1)
        self._joystick = pygame.joystick.Joystick(0)
        logger.debug("Found", self._joystick.get_name())
        self._joystick.init()
        self._stopped = False

    def handle_left_stick_h(self, event):
        pass

    def handle_left_stick_v(self, event):
        pass

    def handle_right_stick_h(self, event):
        pass

    def handle_right_stick_v(self, event):
        pass

    def handle_left_buttons_n(self, event):
        pass

    def handle_left_buttons_e(self, event):
        pass

    def handle_left_buttons_s(self, event):
        pass

    def handle_left_buttons_w(self, event):
        pass

    def handle_right_buttons_n(self, event):
        pass

    def handle_right_buttons_e(self, event):
        pass

    def handle_right_buttons_s(self, event):
        pass

    def handle_right_buttons_w(self, event):
        pass

    def run(self):
        while not self._stopped:
            for event in pygame.event.get():
                logger.info(event)
                if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.05:
                    handler = self.stick_handlers.get(event.axis)
                elif event.type == pygame.JOYBUTTONDOWN:
                    handler = self.button_handlers.get(event.button)
                if handler:
                    function = getattr(self, "handle_%s" % handler)
                    function(event)

j = Joystick()
j.run()
