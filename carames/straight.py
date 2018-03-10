from gpiozero import Robot
from time import sleep
robot = Robot(left = (7, 8), right = (9, 10))
while True:
        robot.forward(0.1)
        sleep(3)
        robot.stop()

        
        
