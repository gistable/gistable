#! /usr/bin/python

import time
import threading

def f():
    for x in range(10):
        print "I am alive and running"
        time.sleep(0.1)


thread = threading.Thread(target=f)
thread.start()
time.sleep(0.5)
print "Stopping the thread"
thread._Thread__stop()
print "Stopped the thread"
time.sleep(1)


# On my system this gives the following output:
# torsten@sharokan:~$ python demo.py 
# I am alive and running
# I am alive and running
# I am alive and running
# I am alive and running
# I am alive and running
# Stopping the thread
# Stopped the thread
# I am alive and running
# I am alive and running
# I am alive and running
# I am alive and running
# I am alive and running
