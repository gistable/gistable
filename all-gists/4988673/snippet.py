#!/usr/bin/python

# A Pomodoro timer!
# Built for the Raspberry Pi
# 
# http://en.wikipedia.org/wiki/Pomodoro_Technique
# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_LEDBackpack/Adafruit_7Segment.py
# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_LEDBackpack/Adafruit_LEDBackpack.py
# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py
# 
# Author Ando Roots <ando@sqroot.eu> 2013

import time, sys, datetime
from Adafruit_7Segment import SevenSegment
import RPi.GPIO as GPIO

class Pomodoro:
	
	# Button to start / pause the timer
	BUTTON_START = 18
	
	# Button to reset everything
	BUTTON_RESET = 25
	
	# LED pins that show the number of completed Pomodoros
	LED_1 = 23
	LED_2 = 17
	LED_3 = 22
	LED_4 = 4
	
	# Two states: running or paused
	STATUS_RUNNING = 0
	STATUS_STANDBY = 1
	
	POMODORO_LENGTH = 1500 # 25 minutes
	
	# State variables
	current_status = STATUS_STANDBY
	elapsed_seconds = 0
	pomodoros_completed = 0
	
	# 7-segment display (run i2cdetect -y 1 to get the addr)
	segment = SevenSegment(address=0x70)
	
	def __init__(self):
		self.output("Running the program - press Ctrl + C to exit.")
		
		GPIO.setmode(GPIO.BCM)
		
		GPIO.setup(self.BUTTON_START,GPIO.IN)
		GPIO.setup(self.BUTTON_RESET,GPIO.IN)
		
		GPIO.setup(self.LED_1, GPIO.OUT)
		GPIO.setup(self.LED_2, GPIO.OUT)
		GPIO.setup(self.LED_3, GPIO.OUT)
		GPIO.setup(self.LED_4, GPIO.OUT)
		
		self.clear_LEDs()
		self.output("Initialized. Press START/PAUSE to begin.")
		
	def is_button_pressed(self, pin_number):
		return GPIO.input(pin_number)
	
	def clear_LEDs(self):
		GPIO.output(self.LED_1, False)
		GPIO.output(self.LED_2, False)
		GPIO.output(self.LED_3, False)
		GPIO.output(self.LED_4, False)
		
	# Write a 4-digit number to the LCD
	def write_number(self, value):
		value = int(value)
		if value > 9999:
			print "Value %s is out of bounds, setting to 9999" % value
			value = 9999
		value = str(value).zfill(4)
		self.segment.writeDigit(0, int(value[0]))
		self.segment.writeDigit(1, int(value[1]))
		self.segment.writeDigit(3, int(value[2]))
		self.segment.writeDigit(4, int(value[3]))
		return self		
		
	def get_pressed_button(self):
		if self.is_button_pressed(self.BUTTON_START):
			return self.BUTTON_START
		if self.is_button_pressed(self.BUTTON_RESET):
			return self.BUTTON_RESET
		return None
	
	def output(self, text):
		current_time = time.strftime("%H:%M:%S", time.gmtime())
		print "[%s] %s" % (current_time, text)
		
	def reset(self):
		self.output("Reset - press START/PAUSE to run.")
		self.current_status = self.STATUS_STANDBY
		self.pomodoros_completed = 0
		self.elapsed_seconds = 0
		self.clear_LEDs()
		self.segment.disp.clear()
		self.segment.setColon(0)
	
	def start(self):
		self.output("Starting...")
		self.current_status = self.STATUS_RUNNING
	
	def standby(self):
		if self.current_status is self.STATUS_STANDBY:
			self.output("Continuing")
			self.current_status = self.STATUS_RUNNING
		else:
			self.output("Standby mode - press START/PAUSE to continue.")
			self.current_status = self.STATUS_STANDBY
		self.segment.setColon(GPIO.IN)
	
	def process_button_presses(self):
		pressed_btn = self.get_pressed_button()
		if pressed_btn is None:
			return
	
		if pressed_btn is self.BUTTON_RESET:
			self.reset()
		else:
			if self.current_status is self.STATUS_STANDBY:
				self.start()
			else:
				self.standby()
			
		# Debounce
		time.sleep(0.05)
		
		# Wait for the button to be released
		while self.get_pressed_button() is not None:
			time.sleep(0.05)
	
	def seconds_to_hm(self, seconds):
		time_string = str(datetime.timedelta(seconds=seconds))
		return time_string[2:4] + time_string[5:7]
	
	# Light N number of LEDs
	def activate_n_LEDs(self, no_of_LEDs):
		self.clear_LEDs()
		if no_of_LEDs is 1:
			GPIO.output(self.LED_1, True)
		elif no_of_LEDs is 2:
			GPIO.output(self.LED_1, True)
			GPIO.output(self.LED_2, True)
		elif no_of_LEDs is 3:
			GPIO.output(self.LED_1, True)
			GPIO.output(self.LED_2, True)
			GPIO.output(self.LED_3, True)
		else:
			GPIO.output(self.LED_1, True)
			GPIO.output(self.LED_2, True)
			GPIO.output(self.LED_3, True)
			GPIO.output(self.LED_4, True)
		
	def complete_pomodoro(self):
		if self.pomodoros_completed == 4:
			self.output("Four Pomodoros completed! Time for a longer break.")
			self.reset()
			return
		
		self.pomodoros_completed += 1
		self.elapsed_seconds = 0
		self.output("Pomodoro no #%s completed! Take a short break and press the START/PAUSE when you return." % self.pomodoros_completed)
		self.activate_n_LEDs(self.pomodoros_completed)
		self.segment.disp.clear()
		
		self.current_status = self.STATUS_STANDBY
		self.segment.setColon(0)
		
	# Main loop
	def run(self):
		
		elapsed_seconds = 0
		
		while True:
			
			# Check for reset / start / pause btn press
			self.process_button_presses()
		
			# Whether we need to complete the current Pomodoro
			if self.elapsed_seconds >= self.POMODORO_LENGTH:
				self.complete_pomodoro()
				continue
			
			# Increase timer when the status is running
			if self.current_status is self.STATUS_RUNNING:
				self.elapsed_seconds += 1
				display_value = self.seconds_to_hm(self.elapsed_seconds)
				self.write_number(display_value)
				self.output(display_value)
				
				if self.elapsed_seconds % 2 is 0:
					self.segment.setColon(GPIO.OUT)
				else:
					self.segment.setColon(GPIO.IN)
				
			time.sleep(1)
			
		    
    # Cleanup on exit
	def __del__(self):
		self.segment.disp.clear()
		GPIO.cleanup()
		
		
# Run the program
pomodoro = Pomodoro().run()