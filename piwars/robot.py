# coding: utf-8
import logging
import time

from .vendor.piborg.thunderborg import ThunderBorg
from .vendor.piborg.ultraborg import UltraBorg

class RobotError(Exception): pass



class Robot(object):

    max_power_factor = 1
    default_power = 0.5
    front = -1
    back = +1

    degree15_secs = 0.53
    cm10_secs = 0.671

    def __init__(self, i2cAddress=0x15):
        self.logger = logging.getLogger("Robot")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())

        self.tb = ThunderBorg.ThunderBorg()
        self.tb.i2cAddress = i2cAddress
        self.tb.Init()
        if not self.tb.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if not boards:
                raise RobotError("No ThunderBorg found")
            else:
                raise RobotError("No board found at %s; but found at %s" % (i2cAddress, ", ".join(board)))

        self.ub = UltraBorg.UltraBorg()
        self.ub.Init()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.logger.info("Shutting down")
        self.tb.MotorsOff()

    def _motor1(self, power):
        self.logger.info("Motor 1 -> %1.2f", power)
        self.tb.SetMotor1(power)

    def _motor2(self, power):
        self.logger.info("Motor 2 -> %1.2f", power)
        self.tb.SetMotor2(power)

    def _motors(self, power):
        self.logger.info("Motors -> %1.2f", power)
        if power == 0:
            self.tb.MotorsOff()
        else:
            self.tb.SetMotors(power)

    def get_right_mm(self):
        return self.ub.GetDistance3()

    def get_left_mm(self):
        return self.ub.GetDistance4()

    def get_front_mm(self):
        return self.ub.GetDistance1()

    def get_left_speed(self):
        return self.tb.GetMotor2() / self.max_power_factor

    def get_right_speed(self):
        return self.tb.GetMotor1() / self.max_power_factor

    def forwards(self, lpower=default_power, rpower=default_power):
        if lpower == rpower:
            self._motors(self.front * self.max_power_factor * lpower)
        else:
            self._motor1(self.front * self.max_power_factor * rpower)
            self._motor2(self.front * self.max_power_factor * lpower)

    def backwards(self, lpower=default_power, rpower=default_power):
        if lpower == rpower:
            self._motors(self.back * self.max_power_factor * lpower)
        else:
            self._motor1(self.back * self.max_power_factor * rpower)
            self._motor2(self.back * self.max_power_factor * lpower)

    def go(self, left_power=default_power, right_power=default_power):
        self._motor1(self.front * self.max_power_factor * right_power)
        self._motor2(self.front * self.max_power_factor * left_power)

    def turn_right(self, power=default_power, n_secs=None):
        self.go(power, -power)
        if n_secs is not None:
            time.sleep(n_secs)
            self.stop()

    def turn_left(self, power=default_power):
        self.go(-power, +power)

    def stop(self):
        self._motors(0)

    def turn_through(self, n_degrees):
        self.turn_right()
        n_secs = (n_degrees / 15) * self.degree15_secs
        time.sleep(n_secs)
        #~ self.stop()

    def forwards_for(self, n_cms):
        self.forwards()
        n_secs = (n_cms / 10) * self.cm10_secs
        time.sleep(n_secs)
        self.stop()

    def set_led(self, n, rgb):
        rgb = rbg.lstrip("#")
        r = int(rgb[0:2], 16) / 255.0
        g = int(rgb[2:4], 16) / 255.0
        b = int(rgb[4:6], 16) / 255.0
        if n == 1:
            self.tb.SetLed1(r, g, b)
        elif n == 2:
            self.tb.SetLed2(r, g, b)
        else:
            raise RobotError("Invalid LED number: %s" % n)

    def get_led(self, n):
        if n == 1:
            r, g, b = self.tb.GetLed1()
        elif n == 2:
            r, g, b = self.tb.GetLed2()
        else:
            raise RobotError("Invalid LED number: %s" % n)
        return "#" + "".join("%02x" % (i * 255.0) for i in (r, g, b))

    def _get_battery_level(self):
        return self.tb.GetBatteryReading()
    battery_level = property(_get_battery_level)


if __name__ == '__main__':
    import time
    with Robot() as robbie:
        logger = logging.getLogger("Robot")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        robbie.forwards()
        time.sleep(1)
        robbie.backwards()
        time.sleep(1)
        robbie.turn_left()
        time.sleep(2)
        robbie.forwards()
        time.sleep(1)
        robbie.turn_right()
        time.sleep(2)
        robbie.stop()
