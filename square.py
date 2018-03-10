from piwars import robot
from time import sleep

DEGREE15_SECS = 0.53
CM10_SECS = 0.671
def turn_through(robbie, n_degrees):
    robbie.turn_right()
    n_secs = (n_degrees / 15) * DEGREE15_SECS
    print(n_degrees, n_secs)
    sleep(n_secs)

def forwards_for(robbie, n_cms):
    robbie.forwards()
    n_secs = (n_cms / 10) * CM10_SECS
    sleep(n_secs)


def square(robbie):
    for i in range(2):
        robbie.forwards()
        sleep(1)
        turn_through(robbie, 90)

def octagon(robbie):
    for i in range(8):

        robbie.forwards()
        sleep(1)
        turn_through(robbie, 45)

def line(robbie):
    forwards_for(robbie, 13)



if __name__ == '__main__':
    with robot.Robot() as robbie:
        line(robbie)