from gpiozero import DistanceSensor, Robot
from time import sleep
robot = Robot (left=(7,8), right=(9,10))
#robot.forward(0.3)

def go_forward(n_seconds):
    robot.forward(0.5)
    sleep(n_seconds)
    robot.stop()

def go_left(n_seconds):
    robot.left(0.5)
    sleep(n_seconds)
    robot.stop()

def go_right(n_seconds):
    robot.right(0.5)
    sleep(n_seconds)
    robot.stop()
    
sensor = DistanceSensor(echo=18, trigger=17)
robot.forward(0.3)
while True:
    #print('Distance:', sensor, distance)
    if sensor.distance > 0.01:
       robot.forward(0.4) 
    if sensor.distance < 0.1:
       print("i am too close") 
       robot.left(0.25)
    if sensor.distance > 0.1:
       print("opps iam going too far")
       robot.right(0.25)
robot.stop()


go_forward(0.2)
go_left(0.25)
go_right(0.25)


    


    
