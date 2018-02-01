# serial data dumper for Jack and Dirty Dan
# Assumes that all formatting (comma separated) happens on the arduino
# and assumes that the arduino is probably using serial.print() to send
# the data over the serial port and assumes that the OS is windows

import serial
from datetime import datetime
import msvcrt

# change to match COM port
port = 'COM3'

# change to match baud rate
br = 115200

# open serial port
ser = serial.Serial(port,br)
ser.open()

# change if you want
extension = '.csv'
# create timestampped file
filename = 'data_' + datetime.now().strftime('%Y%m%d_%X') + extension

# open said file
fop = open(filename, 'w')

# create header if you want
# uncomment and change to suit your needs
# fop.write('DATA1,DATA2,')
print 'Press any key to exit...'
while not msvcrt.kbhit():
	if ser.inWaiting():
		data = ser.read(ser.inWaiting())
		# display received data in console since you won't be
    		# able to use the arduino console at the same time
		print data,
		# write data to file assumes all formatting takes place on arduino
		# like commas, newlines, and crap
		fop.write(data)

# clean up	
fop.close()
ser.close()
