#!/usr/bin/python3

from collections import deque
from time import sleep
from os import system

def tilt():
    with open('/sys/devices/platform/lis3lv02d/position') as f:
        return int(f.read().split(",")[1])

buf = deque([], 32)
for i in range(buf.maxlen):
    buf.append(tilt())
    sleep(0.01)

state = "normal"
newstate = state

while True:
    buf.append(tilt())
    avg = sum(buf) // buf.maxlen
    if state == "normal":
        if avg < -800:
            newstate = "right"
        if avg > 800:
            newstate = "left"
    elif state == "right":
        if avg > -500:
            newstate = "normal"
    elif state == "left":
        if avg < 500:
            newstate = "normal"
    if state != newstate:
            system("xrandr --output LVDS-0 --rotate " + newstate)
    state = newstate
    sleep(0.04)