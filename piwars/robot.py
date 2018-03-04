# coding: utf-8
from .vendor.piborg.thunderbord import ThunderBorg
from .vendor.piborg.ultraborg import UltraBorg

class RobotError(Exception): pass

class Robot(object):

    def __init__(self, i2cAddress=0x15):
        self.tb = ThunderBorg.ThunderBorg()
        self.tb.i2cAddress = i2cAddress
        self.tb.Init()
        if not self.tb.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if not boards:
                raise RobotError("No ThunderBorg found")
            else:
                raise RobotError("No board found at %s; but found at %s" % (i2cAddress, ", ".join(board))

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
        return self.tb.GetMotor1() * 100.0

    def get_right_speed_percent(self):
        return self.tb.GetMotor2() * 100.0

    def forwards_left(self, power_percent):
        self.tb.SetMotor1(power / 100.0)

    def forwards_right(self, power_percent):
        self.tb.SetMotor2(power_percent / 100.0)

    def forwards(self, power_percent):
        self.tb.SetMotors(power_percent / 100.0)

    def backwards_left(self, power_percent):
        self.tb.SetMotor1(-power_percent / 100.0)

    def backwards_right(self, power_percent):
        self.tb.SetMotor2(-power_percent / 100.0)

    def backwards(self, power_percent):
        self.tb.SetMotors(power_percent / 100.0)

    def stop_left(self):
        self.tb.SetMotor1(0)

    def stop_right(self):
        self.tb.SetMotor1(0)

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
        return "".join("%02x" % (i * 255.0) for i in r, g, b)


    def battery_level(self):
        return self.tb.GetBatteryReading()

