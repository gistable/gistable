# Tkinter and GPIO together

from Tkinter import *
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, GPIO.LOW)

def toggle():
  if GPIO.input(24):
		GPIO.output(24, GPIO.LOW)
		toggleButton["text"] = "Turn LED On"
	else:
		GPIO.output(24, GPIO.HIGH)
		toggleButton["text"] = "Turn LED Off"

root = Tk()
root.title("Toggler")
toggleButton = Button(root, text="Turn LED On", command=toggle)
toggleButton.pack(side=LEFT)

quitButton = Button(root, text="Quit", command=exit)
quitButton.pack(side=LEFT)

root.mainloop()