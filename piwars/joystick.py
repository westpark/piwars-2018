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

class EventMap(object):

    _events = {
        "left_stick_h" : (pygame.JOYAXISMOTION, 2),
        "left_stick_v" : (pygame.JOYAXISMOTION, 1),
        "right_stick_h" : (pygame.JOYAXISMOTION, 2),
        "right_stick_v" : (pygame.JOYAXISMOTION, 3),
    }

    def __init__(self):
        self._event_map = {}
        self._lock = threading.Lock()

    def __setattr__(self, attr, value):
        if attr in self._events:
            with self._lock:
                self._event_map[attr] = value
        else:
            raise AttributeError

    def __getattr__(self, attr):
        if attr in self._events:
            with self._lock:
                return self._event_map.get(attr)
        else:
            raise AttributeError

class Joystick(object):

    _events = {
        "left_stick_h" : (pygame.JOYAXISMOTION, 2),
        "left_stick_v" : (pygame.JOYAXISMOTION, 1),
        "right_stick_h" : (pygame.JOYAXISMOTION, 2),
        "right_stick_v" : (pygame.JOYAXISMOTION, 3),
    }

    def __init__(self):
        logger.debug("Waiting for joystick...")
        pygame.joystick.init()
        while pygame.joystick.get_count() < 1:
            time.sleep(0.1)
        self._joystick = pygame.joystick.Joystick(0)
        logger.debug("Found", self._joystick.get_name())
        self._joystick.init()

        self._event_handlers = {}
        self._event_lock = threading.Lock()

    def set_event(self, event_name, function):
        if event_name not in self._events:
            raise RuntimeError("No such event: %s" % event_name)
        pygame_event, key = self._events[event_name]
        with self._event_lock:
            self._event_handlers.setdefault(pygame_event, {})[key] = function

    def find_handler(self, pygame_event, key):
        with self._event_lock:
            return self._event_handlers.get(pygame_event, {}).get(key)

    def handle_axis(self, event):
        handler = self.find_handler(pygame.JOYAXISMOTION, event.axis)
        if handler:
            logger.info("Running handler %s for %s", handler, event)
            handler(event.value)

    def handle_button(self, event):
        handler = self.find_handler(pygame.JOYBUTTONDOWN, event.button)
        if handler:
            logger.info("Running handler %s for %s", handler, event)
            handler()

    def run(self):
        while True:
            for event in pygame.event.get():
                logger.info(event)
                if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.05:
                    self.handle_axis(event)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.handle_button(event)

def left_stick_h(movement):
    print("Movement on left stick:", movement)

j = Joystick()
j.set_event("left_stick_h", left_stick_h)
j.run()
