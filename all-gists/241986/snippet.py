from create import *
from time import *
import create

robot = create.Create(3)

def wait():
    sleep(.5)
    
def die():
    robot.turn(1024,180)

##def song():
##    wait()
    
def main():
    y = 0
##    song()
    while y != 2:
        robot.go(1000)
        right = robot.sensors([101])
        left = robot.sensors([102])
        left_bumper = left[101]
        right_bumper = right[102]
        if left_bumper == 1 and right_bumper == 1:
             robot.stop()
            wait()
            robot.turn(180,180)
            wait()
            y = y+1
        elif left_bumper == 1:
            robot.stop ()
            wait()
            robot.turn(-90,180)
            wait()
            y = y+1
        elif right_bumper == 1:
             robot.stop ()
            wait()
            robot.turn(90.180)
            wait()
            y = y+1
        wait()
    die()
main()