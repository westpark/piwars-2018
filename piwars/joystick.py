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

class Joystick(object):

    stick_handlers = {
        0 : "left_stick_h",
        1 : "left_stick_v",

        2 : "right_stick_h",
        3 : "right_stick_v",
    }
    button_handlers = {
        4 : "left_quadrant_n",
        5 : "left_quadrant_e",
        6 : "left_quadrant_s",
        7 : "left_quadrant_w",

        12 : "right_quadrant_n",
        13 : "right_quadrant_e",
        14 : "right_quadrant_s",
        15 : "right_quadrant_w",

        0 : "select",
        3 : "start"

        10 : "front_left_upper",
        8 : "front_left_lower",
        11 : "front_right_upper",
        9 : "front_right_lower",
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

    def run_once(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.05:
                handler = self.stick_handlers.get(event.axis)
            elif event.type == pygame.JOYBUTTONDOWN:
                handler = self.button_handlers.get(event.button)
            else:
                handler = None
            if handler:
                function = getattr(self, "handle_%s" % handler, None)
                if function:
                    logger.info("%s for %s", function, event)
                    function(event)

    def run(self):
        while not self._stopped:
            self.run_once()
