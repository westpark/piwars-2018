# coding: utf-8
import logging
import time

from .vendor.piborg.thunderborg import ThunderBorg
from .vendor.piborg.ultraborg import UltraBorg

class RobotError(Exception): pass

class Servo(object):

    def __init__(self, ultraborg, n_servo):
        self.ultraborg = ultraborg
        if not 1 <= n_servo <= 4:
            raise ValueError("Servo must be 1 - 4")
        self.n_servo = n_servo

    def _ub_function(self, base):
        return getattr(self.ultraborg, "%s%d" % (base, self.n_servo))

    def _get_raw_position(self):
        function = self._ub_function("GetRawServoPosition")
        return function()
    raw_position = property(_get_raw_position)

    def _get_position(self):
        function = self._ub_function("GetServoPosition")
        return function()
    def _set_position(self, position):
        function = self._ub_function("SetServoPosition")
        return function(position)
    position = property(_get_position, _set_position)

    def _get_min(self):
        function = self._ub_function("GetServoMinimum")
        return function()
    def _set_min(self, pwm_level):
        function = self._ub_function("SetServoMinimum")
        return function(pwm_level)
    min = property(_get_min, _set_min)

    def _get_max(self):
        function = self._ub_function("GetServoMaximum")
        return function()
    def _set_max(self, pwm_level):
        function = self._ub_function("SetServoMaximum")
        return function(pwm_level)
    max = property(_get_max, _set_max)

    def _get_startup(self):
        function = self._ub_function("GetServoStartup")
        return function()
    def _set_startup(self, pwm_level):
        function = self._ub_function("SetServoStartup")
        return function(pwm_level)
    startup = property(_get_startup, _set_startup)

    def calibrate(self, pwm_level):
        function = self._ub_function("CalibrateServoPosition")
        return function(pwm_level)



class Robot(object):

    max_power_factor = 1
    default_power = 0.5
    front = -1
    back = +1

    #
    # How many seconds does it take to describe a full rotation at full power?
    #
    full_power_degree360_secs = 2.12

    cm10_secs = 0.671

    def __init__(self, i2cAddress=0x15):
        self.logger = logging.getLogger("Robot")
        self.logger.setLevel(logging.INFO)
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

        self.servos = [Servo(self.ub,n) for n in range(1, 5)]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.logger.info("Shutting down")
        self.tb.MotorsOff()
        for servo in self.servos:
            servo.position = 0

    def _motor1(self, power):
        self.logger.debug("Motor 1 -> %1.2f", power)
        self.tb.SetMotor1(power)

    def _motor2(self, power):
        self.logger.debug("Motor 2 -> %1.2f", power)
        self.tb.SetMotor2(power)

    def _motors(self, power):
        self.logger.debug("Motors -> %1.2f", power)
        if power == 0:
            self.tb.MotorsOff()
        else:
            self.tb.SetMotors(power)

    def get_right_mm(self):
        return self.ub.GetDistance1()

    def get_left_mm(self):
        return self.ub.GetDistance2()

    def get_front_mm(self, use_raw=False):
        if use_raw:
            return self.ub.GetRawDistance4()
        else:
            return self.ub.GetDistance4()

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

    def turn_right(self, n_secs=None, power=default_power):
        self.go(+power, -power)
        if n_secs is not None:
            time.sleep(n_secs)
            self.stop()

    def turn_left(self, n_secs=None, power=default_power):
        self.go(-power, +power)
        if n_secs is not None:
            time.sleep(n_secs)
            self.stop()

    def stop(self):
        self._motors(0)

    def turn_through(self, n_degrees, power=default_power):
        #
        # In fact, at full power we slightly overshoot so we probably
        # want to dampen the number a little as we approach higher power
        #
        dampener_factor = 0.85 if power > 0.5 else 1
        n_secs = dampener_factor * (abs(n_degrees) / 360) * self.full_power_degree360_secs / power
        print("Turning through", n_degrees, "for", n_secs)
        if n_degrees > 0:
            self.turn_right(n_secs, power)
        else:
            self.turn_left(n_secs, power)

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

    def _check_servo(self, n_servo):
        if not 1 <= n_servo <= 4:
            raise ValueError("Servo must be 1-4")

    def move_servo_to(self, n_servo, position):
        """Set the servo position

        0 is central, -1 is maximum left, +1 is maximum right
        """
        self._check_servo(n_servo)
        function = getattr(self.ub, "SetServoPosition%d" % n_servo)
        return function(position)

    def get_servo_min(self, n_servo):
        """pwmLevel = get_servo_min(n_servo)

        Gets the minimum PWM level for servo
        This corresponds to position -1
        The value is an integer where 2000 represents a 1 ms servo burst
        e.g.
        2000  -> 1 ms servo burst, typical shortest burst
        4000  -> 2 ms servo burst, typical longest burst
        3000  -> 1.5 ms servo burst, typical centre
        5000  -> 2.5 ms servo burst, higher than typical longest burst
        """
        self._check_servo(n_servo)
        function = getattr(self.ub, "GetServoMinimum%d" % n_servo)
        return function()

    def get_servo_max(self, n_servo):
        """pwmLevel = get_servo_max(n_servo)

        Gets the maximum PWM level for servo output #2
        This corresponds to position +1
        The value is an integer where 2000 represents a 1 ms servo burst
        e.g.
        2000  -> 1 ms servo burst, typical shortest burst
        4000  -> 2 ms servo burst, typical longest burst
        3000  -> 1.5 ms servo burst, typical centre
        5000  -> 2.5 ms servo burst, higher than typical longest burst
        """
        self._check_servo(n_servo)
        function = getattr(self.ub, "GetServoMaximum%d" % n_servo)
        return function()

    def get_servo_startup(self, n_servo):
        """pwmLevel = get_servo_startup(n_servo)

        Gets the startup PWM level for servo output #1
        This can be anywhere in the minimum to maximum range
        The value is an integer where 2000 represents a 1 ms servo burst
        e.g.
        2000  -> 1 ms servo burst, typical shortest burst
        4000  -> 2 ms servo burst, typical longest burst
        3000  -> 1.5 ms servo burst, typical centre
        5000  -> 2.5 ms servo burst, higher than typical longest burst

        """
        self._check_servo(n_servo)
        function = getattr(self.ub, "GetServoStartup%d" % n_servo)
        return function()

    def calibrate_servo_position(self, n_servo, pwm_level):
        """
        calibrate_servo_position(n_servo, pwm_level)

        Sets the raw PWM level for servo output #1
        This value can be set anywhere from 0 for a 0% duty cycle to 65535 for a 100% duty cycle

        Setting values outside the range of the servo for extended periods of time can damage the servo
        NO LIMIT CHECKING IS PERFORMED BY THIS COMMAND!
        We recommend using the tuning GUI for setting the servo limits for SetServoPosition1 / GetServoPosition1

        The value is an integer where 2000 represents a 1ms servo burst, approximately 3% duty cycle
        e.g.
        2000  -> 1 ms servo burst, typical shortest burst, ~3% duty cycle
        4000  -> 2 ms servo burst, typical longest burst, ~ 6.1% duty cycle
        3000  -> 1.5 ms servo burst, typical centre, ~4.6% duty cycle
        5000  -> 2.5 ms servo burst, higher than typical longest burst, ~ 7.6% duty cycle
        """
        self._check_servo(n_servo)
        function = getattr(self.ub, "CalibrateServoPosition%d" % n_servo)
        return function(pwm_level)

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
