#!/usr/bin/python

import time
import RPi.GPIO as GPIO
from robot_brain.servo import Servo

GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 25
GPIO_ECHO    = 24
k = .7  # filter constant
rotation_filtered = 0
servo = Servo(min=60, max=250)
scalar = 50 # smaller is more finger movement

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO, GPIO.IN)      # Echo

GPIO.output(GPIO_TRIGGER, False)

# Allow module to settle
time.sleep(0.5)

while True:
    # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    while GPIO.input(GPIO_ECHO)==0:
      pass  # wait for pin to go high

    start = time.time()
    while GPIO.input(GPIO_ECHO)==1:
      stop = time.time()
      if (stop - start) > .1:
          break

    # Calculate pulse length
    elapsed = stop - start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34300

    # That was the distance there and back so halve the value
    distance = distance / 2

    # Calculate how much to rotate the servo (scale between 0 and 1)
    rotation = distance / 50
    if rotation > 1:
        rotation = 1
    # A simple moving average filter
    rotation_filtered = k * rotation_filtered + (1.0 - k) * rotation
    rot = 1 - rotation_filtered
    servo.set(rot)
    print 'setting servo to:', rot
    time.sleep(.1)