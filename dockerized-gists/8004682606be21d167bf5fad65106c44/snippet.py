from __future__ import print_function
from threading import Thread
from time import sleep

WALKNUM = 0
STEPNUM = 0
KILL = False

def increment(value):
    global WALKNUM
    global STEPNUM
    while not KILL:
        WALKNUM += value
        STEPNUM += 1

T1 = Thread(target=increment, args=(1, ))
T2 = Thread(target=increment, args=(-1, ))
T1.start()
T2.start()

while not KILL:
    try:
        sleep(1)
        print(str(WALKNUM)+" After "+str(STEPNUM)+" Steps")
    except KeyboardInterrupt:
        KILL = True
