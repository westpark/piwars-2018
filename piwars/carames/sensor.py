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

def go_forward_cautious():
  sensor = DistanceSensor(echo=18, trigger=17)
  robot.forward(0.3)
  while True:
      ##print('Distance: ', sensor.distance)
      if sensor.distance < 0.1:
          ##print("less than 0.1")
          robot.forward(0.5)
      if sensor.distance < 0.5:
          print("less than 0.05")
          robot.forward(0.025)
      if sensor.distance < 0.025:
          print("About to stop")
          robot.stop()
          break

go_forward_cautious()
print("About to go left")
go_left(1)
print("Cautious again")
go_forward_cautious()
