# tom@jitter.eu 12/2017 :*
# https://gist.github.com/gretel/c84643e4d13818fc5a35a8de888126bb

import pycom
import time
from machine import Pin
from machine import PWM

# increments per cycle
STEP_1 = 0.00700
STEP_2 = 0.01200
# on
MAX_VALUE = 1.0
# off
MIN_VALUE = 0.0

# disable bright blue blink
# https://docs.pycom.io/chapter/tutorials/all/rgbled.html
pycom.heartbeat(False)

# setup two inputs
# https://docs.pycom.io/chapter/firmwareapi/pycom/machine/Pin.html
p_in_1 = Pin('P13', mode=Pin.IN, pull=Pin.PULL_UP)
p_in_2 = Pin('P14', mode=Pin.IN, pull=Pin.PULL_UP)

# create two pwm channels for the LEDs
# https://docs.pycom.io/chapter/firmwareapi/pycom/machine/PWM.html
pwm_1 = PWM(0, frequency=100)
pwm_c_1 = pwm_1.channel(0, pin='P10', duty_cycle=1.0)
# purely decorative
pwm_c_2 = pwm_1.channel(1, pin='P11', duty_cycle=1.0)

# piggyback buzzer to channel 0 (which drives the first led)
pwm_buz = pwm_1.channel(0, pin='P9', duty_cycle=0.5)

# initialize variables
c_1_cycle = MIN_VALUE
c_2_cycle = MIN_VALUE
cstep_1 = STEP_1
cstep_2 = STEP_2

# loop
while True:
  # button 1 effect
  if p_in_1() == 1:
    delay = 5
  else:
    delay = 50

  # button 2 effect
  if p_in_2() == 1:
    # swap values
    temp = c_2_cycle
    c_2_cycle = c_1_cycle
    c_1_cycle = temp
    del temp
    time.sleep_ms(delay * 2)

  # set pulse width
  pwm_c_1.duty_cycle(c_1_cycle)
  pwm_c_2.duty_cycle(c_2_cycle)
  time.sleep_ms(delay)

  # incremenet/decrement
  c_1_cycle += cstep_1
  c_2_cycle += cstep_2

  # boundaries
  if c_1_cycle >= MAX_VALUE:
    cstep_1 = STEP_1 * -1
  elif c_1_cycle <= MIN_VALUE:
    cstep_1 = STEP_1

  if c_2_cycle >= MAX_VALUE:
    cstep_2 = STEP_2 * -1
  elif c_2_cycle <= MIN_VALUE:
    cstep_2 = STEP_2
