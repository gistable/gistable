#!/usr/bin/python
# time module is needed for sleep function:
import time

# Open up the pins and set mode in/out
# TODO: Error handling
setupPin = file("/sys/class/gpio/export", "w")
setupPin.write("%d" % (38)) 
setupPin.close()

setupPin = file("/sys/class/gpio/gpio38/direction", "w")
setupPin.write("out")
setupPin.close()

setupPin = file("/sys/class/gpio/export", "w")
setupPin.write("%d" % (70))
setupPin.close()

setupPin = file("/sys/class/gpio/gpio70/direction", "w")
setupPin.write("in")
setupPin.close()

#Open outPin for writing and inPin for reading:
outPin = file("/sys/class/gpio/gpio38/value", "w")
inPin = file("/sys/class/gpio/gpio70/value", "r")

try:
    	while True:
		# This method uses polling to read the state of the pin.
		# It's not the way it should be done, but we'll make do
		# with this for now. 
    		inPin.seek(0)
    		if inPin.read() =="1\n":
			print "Button Pressed!\n"
                	outPin.write("1")
                	outPin.flush()
                	time.sleep(1)

                	outPin.write("0")
                	outPin.flush()
		# don't peg the processor:
		time.sleep(.1)
# Control+C will get us out of that loop and close the pins so that other apps can use:        		
except KeyboardInterrupt:
        inPin = file("/sys/class/gpio/unexport", "w")
        inPin.write("%d" % (38))
        inPin.close()

	outPin = file("/sys/class/gpio/unexport", "w")
	outPin.write("%d" % (70))
	inPin.close()
