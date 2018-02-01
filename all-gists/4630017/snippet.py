#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script toggles lights on and off using the phue library and a physical switch
It is started on boot in /etc/rc.local with this line:
python /home/pi/light_button_control/light_button_control.py &
'''

from time import sleep
import RPi.GPIO as GPIO
import time
from phue import Bridge

GPIO.setmode(GPIO.BCM)
GPIO.setup(7, GPIO.IN)

b = Bridge()

def toggle_lights():
    lights = b.get_light_objects()
    on = False
    for light in lights:
        if light.on:
            on = True
            break
    if on:
        b.set_group(0,'on',False)
    else:
        b.set_light(['Entrée','Frigo','Chambre'],'on',True)

prev_input = 0
while True:
  #take a reading
  input = GPIO.input(7)
  #if the last reading was low and this one high, print
  if ((not prev_input) and input):
    print("Button pressed")
    toggle_lights()
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.05)
