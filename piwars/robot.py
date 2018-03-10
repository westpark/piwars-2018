# coding: utf-8
import logging

from .vendor.piborg.thunderborg import ThunderBorg
from .vendor.piborg.ultraborg import UltraBorg

class RobotError(Exception): pass

class Robot(object):

    max_power_factor = 0.5
    default_power_percent = 75.0
    front = -1
    back = +1
    
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

    def get_left_speed_percent(self):
        return self.tb.GetMotor2() * 100.0 / self.max_power_factor

    def get_right_speed_percent(self):
        return self.tb.GetMotor1() * 100.0 / self.max_power_factor

    def forwards_left(self, power_percent=default_power_percent):
        self._motor2(self.front * self.max_power_factor * power_percent / 100.0)

    def forwards_right(self, power_percent=default_power_percent):
        self._motor1(self.front * self.max_power_factor * power_percent / 100.0)

    def forwards(self, power_percent=default_power_percent):
        self._motors(self.front * self.max_power_factor * power_percent / 100.0)

    def backwards_left(self, power_percent=default_power_percent):
        self._motor2(self.back * self.max_power_factor * power_percent / 100.0)

    def backwards_right(self, power_percent=default_power_percent):
        self._motor1(self.back * self.max_power_factor * power_percent / 100.0)

    def backwards(self, power_percent=default_power_percent):
        self._motors(self.back * self.max_power_factor * power_percent / 100.0)
    
    def go(self, left_power_percent=default_power_percent, right_power_percent=default_power_percent):
        self._motor1(self.front * self.max_power_factor * right_power_percent / 100.0)
        self._motor2(self.front * self.max_power_factor * left_power_percent / 100.0)

    def stop_left(self):
        self._motor2(0)

    def stop_right(self):
        self._motor1(0)
    
    def turn_right(self, power_percent=default_power_percent):
        self.forwards_left(power_percent)
        self.backwards_right(power_percent)

    def turn_left(self, power_percent=default_power_percent):
        self.backwards_left(power_percent)
        self.forwards_right(power_percent)
    
    def stop(self):
        self._motors(0)

    def set_led(self, n, rgb):
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
        return "".join("%02x" % (i * 255.0) for i in (r, g, b))

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
        robbie.stop()
