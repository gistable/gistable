#!/usr/bin/env python

import RPi.GPIO as gpio
from time import sleep
import re
import sys

gpio.setmode(gpio.BCM)
red = 23
yel = 24
grn = 25
lit = 22
on = red
blink = .05

def fastflash(pin):
    for i in range(3):
        gpio.output(pin, gpio.HIGH)
        sleep(blink)
        gpio.output(pin, gpio.LOW)
        sleep(blink)

def setup(lights):
    for pin in lights:
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, gpio.LOW)

def main():
    global on
    setup([red, yel, grn, lit])
    while True:
        line = sys.stdin.readline()
        gpio.output(lit, gpio.HIGH)
        sleep(blink)
        gpio.output(lit, gpio.LOW)
        match = re.match(r'.*? time ?= ?(\d+)(?:\.\d+)? ?ms.*', line)

        if not match or len(match.group(1)) < 1:
            gpio.output(on, gpio.LOW)
            fastflash(red)
            on = red
        elif len(match.group(1)) <= 2:
            gpio.output(on, gpio.LOW)
            gpio.output(grn, gpio.HIGH)
            on = grn
        elif len(match.group(1)) == 3:
            gpio.output(on, gpio.LOW)
            gpio.output(yel, gpio.HIGH)
            on = yel
        else:
            gpio.output(on, gpio.LOW)
            gpio.output(red, gpio.HIGH)
            on = red

if __name__ == '__main__':
    try:
        main()
    finally:
        gpio.cleanup()