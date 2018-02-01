#!/usr/bin/python

# open/close CD/DVD tray from Raspberry Pi GPIO via H-Bridge

import RPi.GPIO as GPIO
import time
import sys
import signal

GPIO.setmode(GPIO.BOARD)

# open/close switches on CD/DVD tray
OPSW = 22 # G25
CLSW = 37 # G26

# H-bridge 2-bit control input, where:
#  K1  K3
#  K2  K4
# K1 = C
# K2 = not (C or D)
# K3 = not (C or D)
# K4 = C
# therefore:
# D C  K1 K2 K3 K4  operation
# 0 0   0  1  1  0  forward
# 0 1   1  0  0  1  reverse
# 1 0   0  0  0  0  coast
# 1 1   1  0  0  1  reverse
C = 38 # G20
D = 40 # G21

# status LEDs
LED_Y = 32 # G12
LED_B = 33 # G13

GPIO.setwarnings(False)
GPIO.setup([OPSW, CLSW], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(C, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(D, GPIO.OUT, initial=GPIO.HIGH) # "disable" by default
GPIO.setup([LED_Y, LED_B], GPIO.OUT, initial=GPIO.HIGH)

def open():
	# forward
	print "opening"
	GPIO.output(C, False)
	GPIO.output(D, False)

def close():
	# reverse
	print "closing"
	GPIO.output(D, False) # set first
	GPIO.output(C, True)
	#GPIO.output(D, False)

def coast():
	print "coasting"
	GPIO.output(C, False)
	GPIO.output(D, True)


def closed():
	return not GPIO.input(CLSW)

def opened():
	return not GPIO.input(OPSW)

def handle(pin):
	value = GPIO.input(pin)

	if pin == OPSW:
		GPIO.output(LED_Y, value)
	elif pin == CLSW:
		GPIO.output(LED_B, value)

def emergency_coast(ignored):
	print "timed out, coasting"
	coast()

limit = 0
direction = None
if len(sys.argv) > 1:
	if sys.argv[1] == '-h':
		sys.stderr.write("""usage: %s [limit] [direction]
\tlimit: maximum number of seconds to drive [default: 0=until done]
\tdirection: direction to drive if if partially open, open/close [default: open]
""" % (sys.argv[0],))
		print
		raise SystemExit

	limit = float(sys.argv[1])
	print "limit",limit
if len(sys.argv) > 2:
	direction = sys.argv[2]
	print "direction",direction

signal.signal(signal.SIGALRM, emergency_coast)
signal.alarm(10)

coast()
GPIO.add_event_detect(OPSW, GPIO.BOTH, handle)
GPIO.add_event_detect(CLSW, GPIO.BOTH, handle)


print "opened=",opened()
print "closed=",closed()

time.sleep(0.1)


if opened():
	close()
elif closed():
	open()
else:
	# partially open, open all the way (unless overridden)
	if direction == 'close':
		close()
	else:
		open()

started = time.time()
for i in range(50):
	time.sleep(0.5)
	if opened():
		print "opened, done"
		break
	if closed():
		print "closed, done"
		break
	elapsed = time.time() - started
	if limit != 0 and elapsed >= limit:
		print "user-specified time limit %s exceeded, done" % (limit,)
		break

coast()
