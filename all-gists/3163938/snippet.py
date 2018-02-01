from Tkinter import *

import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def say_hi():
	print "Lighting up LED"
	GPIO.output(17, GPIO.HIGH)
	time.sleep(5)
	GPIO.output(17, GPIO.LOW)
	
def check_button():
	if (GPIO.input(18) == GPIO.LOW):
		labelText.set("Button Pressed.")
	else:
		labelText.set("")
	root.after(10,check_button)

root = Tk()

button = Button(root, text="Quit.", fg="red", command=quit)
button.pack(side=RIGHT, padx=10, pady=10, ipadx=10, ipady=10)

hi_there = Button(root, text="Light my LED!", command=say_hi)
hi_there.pack(side=LEFT, padx=10, pady=10, ipadx=10, ipady=10)

labelText = StringVar()
labelText.set("Button Pressed.")
label1 = Label(root, textvariable=labelText, height=4)
label1.pack(side=LEFT)

root.title("LED Blinker")
root.geometry('500x300+200+200')

root.after(10,check_button)
root.mainloop()