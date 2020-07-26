#!/usr/bin/env python

import sys, os
from optparse import OptionParser
import Tkinter as tk

# tell python where to find mavlink so we can import it
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../mavlink'))
from pymavlink import mavutil

class App(tk.Frame):
	def __init__(self, tkroot, mavmain):
		tk.Frame.__init__(self, tkroot)
		self.mavmain = mavmain
		self.tkroot = tkroot
		self.validkeys = ['Right', 'Left', 'Up', 'Down']
		self.afterId = dict((k,None) for k in self.validkeys)
		self.keyState = dict((k,False) for k in self.validkeys)
		self.tkroot.bind_all('<Key>', self.keyPressed)
		self.tkroot.bind_all('<KeyRelease>', self.keyReleased)
	def keyPressed(self,event):
		if event.keysym == 'Escape':
			release_rc(self.mavmain)
			self.quit()	
		if event.keysym in self.validkeys:
			if self.afterId[event.keysym] != None:
				self.after_cancel(self.afterId[event.keysym])
				self.afterId[event.keysym] = None
			else:
				self.keyState[event.keysym] = event.time
				processKeyCommand(self.mavmain, self.keyState)
	def keyReleased(self,event):
		if event.keysym in self.validkeys:
			self.afterId[event.keysym] = self.after_idle(self.releaseKey, event)
	def releaseKey(self, event):
		self.afterId[event.keysym] = None
		self.keyState[event.keysym] = False
		processKeyCommand(self.mavmain, self.keyState)

# release control back to the radio
def release_rc(main):
	# a value of 0 releases the control to what the radio says
	values = [ 0 ] * 8
	for i in xrange(1):
		main.mav.rc_channels_override_send(main.target_system, 
			main.target_component, *values)

# attempt to send a control.
# you can pass 0 to refer to what the radio says
# you can pass 0xFFFF to refer to keep the current value 
def send_rc(main, data):
	for i in xrange(1):
		main.mav.rc_channels_override_send(
			main.target_system, main.target_component, *data)
	print ("sending rc: %s"%data)

def processKeyCommand(main, keystate):
	amt = 100
	pitch = 1500
	roll = 1500
	# handle elevator stick
	if keystate['Up']:
		pitch -= amt	# nose down (to go forward)
	if keystate['Down']:
		pitch += amt	# nose up (to go back)
	if pitch == 1500:
		# if this stick is centered, just release it
		pitch = 0
	# handle aile stick
	if keystate['Left']:
		roll -= amt		# roll left
	if keystate['Right']:
		roll += amt		# roll right
	if roll == 1500:
		# if this stick is centered, just release it
		roll = 0
	# set data (0 means channel is released)
	data = [ 0 ] * 8
	data[0] = roll
	data[1] = pitch
	# send the data to the rc override command
	send_rc(main, data)


def main():

	# read command line options
	parser = OptionParser("readdata.py [options]")
	parser.add_option("--baudrate", dest="baudrate", type='int',
					  help="main port baud rate", default=115200)
	parser.add_option("--device", dest="device", default=None, help="serial device")
	parser.add_option("--rate", dest="rate", default=4, type='int', help="requested stream rate")
	parser.add_option("--source-system", dest='SOURCE_SYSTEM', type='int',
					  default=255, help='MAVLink source system for this GCS')
	parser.add_option("--showmessages", dest="showmessages", action='store_true',
					  help="show incoming messages", default=False)
	(opts, args) = parser.parse_args()
	
	if opts.device is None:
		print("You must specify a serial device")
		sys.exit(1)

	# create a mavlink serial instance
	main = mavutil.mavlink_connection(opts.device, baud=opts.baudrate)

	# wait for the heartbeat msg to find the system ID
	main.wait_heartbeat()

	# request data to be sent at the given rate
	main.mav.request_data_stream_send(main.target_system, main.target_component, 
		mavutil.mavlink.MAV_DATA_STREAM_ALL, opts.rate, 1)

	# start up the window to read arrow keys
	tkroot = tk.Tk()
	application = App(tkroot, main)
	tkroot.mainloop()


if __name__ == '__main__':
	main()