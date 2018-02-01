import RPi.GPIO as GPIO
import time
import threading
import signal
import sys
import os

counter = 0
mode = 2
GPIO_num = [22, 18, 16, 15, 13, 12, 11]
GPIO_input = 7
GPIO_val = [False] * len(GPIO_num)
speed = 0.1
debug = False
current_state = 0
previous_state = current_state

def init():
  print "Hi! Pid %s" % os.getpid()
# init
def gpio_init():
  global GPIO_num

  print "Init GPIO"
  GPIO.setmode(GPIO.BOARD)
  for num in GPIO_num:
    GPIO.setup(num, GPIO.OUT)

  GPIO.setup(GPIO_input, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#cleanup
def cleanup():
  print "Cleanup GPIO"
  GPIO.cleanup()

def pattern(counter, n):

  def pattern_binary(counter, n):
    return counter & (1 << n) > 0

  def pattern_binary_blank(counter, n):
    return counter & (1 << n) == 0

  def pattern_move(counter, n):
    return counter % len(GPIO_num) == n

  def pattern_move_backwards(counter, n):
    return counter % len(GPIO_num) == len(GPIO_num) - n - 1

  def pattern_move_blank(counter, n):
    return counter % len(GPIO_num) != n

  def pattern_move_blank_backwards(counter, n):
    return counter % len(GPIO_num) != len(GPIO_num) - n - 1

  global mode, speed 


  if mode == 0:
    return pattern_binary(counter, n)
  elif mode == 1:
    return pattern_binary_blank(counter, n)
  elif mode == 2:
    return pattern_move(counter, n)
  elif mode == 3:
    return pattern_move_backwards(counter, n)
  elif mode == 4:
    return pattern_move_blank(counter, n)
  elif mode == 5:
    return pattern_move_blank_backwards(counter, n)

  raise

def routine():
  global GPIO_num, GPIO_val, counter, mode, speed, current_state, previous_state

  if debug:
    print "%s %s %s %r" % (counter, speed, mode, GPIO_val)

  for i in range(0, len(GPIO_num)):
    GPIO_val[i] = pattern(counter, i)

  for i in range(0, len(GPIO_num)):
    GPIO.output(GPIO_num[i], GPIO_val[i])

  counter = counter + 1

  current_state = GPIO.input(GPIO_input)

  if (current_state and not previous_state):
    mode = (mode + 1) % 6
  if (current_state != previous_state):
    previous_state = current_state


def routine_init():
  try:
    while True:
      routine()
      time.sleep(speed)

  except KeyboardInterrupt:
    cleanup()

init()
gpio_init()
routine_init()

