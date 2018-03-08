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
        self.tb.MotorsOff()

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
        self.tb.SetMotor2(self.front * self.max_power_factor * power_percent / 100.0)

    def forwards_right(self, power_percent=default_power_percent):
        self.tb.SetMotor1(self.front * self.max_power_factor * power_percent / 100.0)

    def forwards(self, power_percent=default_power_percent):
        self.tb.SetMotors(self.front * self.max_power_factor * power_percent / 100.0)

    def backwards_left(self, power_percent=default_power_percent):
        self.tb.SetMotor2(self.back * self.max_power_factor * power_percent / 100.0)

    def backwards_right(self, power_percent=default_power_percent):
        self.tb.SetMotor1(self.back * self.max_power_factor * power_percent / 100.0)

    def backwards(self, power_percent=default_power_percent):
        self.tb.SetMotors(self.back * self.max_power_factor * power_percent / 100.0)
    
    def go(self, left_power_percent=default_power_percent, right_power_percent=default_power_percent):
        if (abs(left_power_percent) > 0.01 or abs(right_power_percent) > 0.01):
            print("left: %3.2f; right: %3.2f" % (left_power_percent, right_power_percent))
        self.tb.SetMotor1(self.front * self.max_power_factor * right_power_percent / 100.0)
        self.tb.SetMotor2(self.front * self.max_power_factor * left_power_percent / 100.0)

    def stop_left(self):
        self.tb.SetMotor2(0)

    def stop_right(self):
        self.tb.SetMotor1(0)
    
    def turn_right(self, power_percent=default_power_percent):
        self.forwards_left(power_percent)
        self.backwards_right(power_percent)

    def turn_left(self, power_percent=default_power_percent):
        self.backwards_left(power_percent)
        self.forwards_right(power_percent)
    
    def stop(self):
        self.tb.MotorsOff()

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

    def battery_level(self):
        return self.tb.GetBatteryReading()


if __name__ == '__main__':
    import time
    with Robot() as robbie:
        #~ robbie.forwards()
        #~ time.sleep(1)
        #~ robbie.backwards()
        #~ time.sleep(1)
        #~ robbie.stop()
        
        robbie.turn_left()
        time.sleep(1)
        robbie.stop()
