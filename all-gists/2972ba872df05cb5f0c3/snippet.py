# -*- coding: utf-8 -*- 
#!/usr/bin/python
import subprocess
import os
import picamera
import time
import shlex
from datetime import datetime
from datetime import timedelta
import datetime as dt
import tgl
import sys 
import RPi.GPIO as GPIO
from functools import partial

ppth = os.path.abspath(__file__)
print ppth

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)
#
our_id = 0
binlog_done = False;
enable_bot = False
#strup_msg = False 

def on_binlog_replay_end():
	binlog_done = True;

def on_get_difference_end():
	pass

def on_our_id(id):
	our_id = id
	return "Set ID: " + str(our_id)

def msg_cb(success, msg):
	pass
	#pp.pprint(success)
	#pp.pprint(msg)

HISTORY_QUERY_SIZE = 100

def history_cb(msg_list, peer, success, msgs):
	print(len(msgs))
	msg_list.extend(msgs)
	print(len(msg_list))
	if len(msgs) == HISTORY_QUERY_SIZE:
		tgl.get_history(peer, len(msg_list), HISTORY_QUERY_SIZE, partial(history_cb, msg_list, peer));

def cb(success):
	print(success)
	print("\ncb function")

def on_msg_receive(msg):
	if msg.out and not binlog_done:
		return;

	global enable_bot
	peer = msg.src
	mystr = msg.text.lower()
	w = mystr.split()
	if (msg.src.id == 97329959):#ADMIN ID
		if (mystr =='dison'):
			enable_bot = True
			peer.send_msg ('Program is Disable.')
			return;
			
		elif (mystr =='disoff'):
			enable_bot = False
			peer.send_msg ('Program is Enable.')
			return;
			
		elif (mystr == 'reboot'):
			peer.send_msg ('Server is Reboot.')
			cmd = 'sudo reboot'
			subprocess.call(cmd.split())
			return;
			
		elif (mystr == 'shutdown'):
			peer.send_msg ('Server is Shutdown.')
			cmd = 'sudo shutdown -h now'
			subprocess.call(cmd.split())		
			return;
		
		elif (w[0] == 'led') and (not(w[1] == None)):
			if (w[1]=='off'):
				peer.send_msg ('Led turned off.')
				GPIO.output(27,0)
				return;
			elif (w[1]=='on'):
				peer.send_msg ('Led turned on.')
				GPIO.output(27,1)
				return;
			else:
				peer.send_msg ('Unknown command.')	
				return;	
			
	
	if (not(enable_bot)):
			if (mystr=='about'):
				peer.send_msg ('Telegram bot v0.1b\n\nProgrammer: @RaminSangesari\nEmail: r_sangsari@yahoo.ca')
				return;
				
			elif (mystr == '!photo'):
				
				path=os.getenv("HOME")
				with picamera.PiCamera() as picam:
					#picam.led = False
					#picam.rotation=90
					picam.framerate = 24
					picam.start_preview()
					picam.annotate_background = picamera.Color('black')
					picam.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					picam.capture(path+'/pic.jpg',resize=(640,480))
					time.sleep(2)
					picam.stop_preview()
					picam.close()
				print(path)	
				peer.send_photo ('/root/pic.jpg')
				peer.send_msg ('Send the picture may take some time.\nPlease wait...')
				return;
				
			elif (mystr == 'id'):
				iid = 'Your telegram id : '+str(msg.src.id)
				peer.send_msg(iid)
				return;
				
			elif (mystr == 'time'):
				ttime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				peer.send_msg (ttime)
				return;					
				
			elif (mystr=='uptime'):
				with open('/proc/uptime', 'r') as f:
					usec = float(f.readline().split()[0])
					usec_str = str(timedelta(seconds = usec))
				peer.send_msg(usec_str)
				return;
			
			elif (mystr == 'help') or (mystr == '?'):
				peer.send_msg ('Commands List:\n\nid\nabout\nuptime\nphoto\ntime\n\nCommands is not case-sensitive.')
				return;
				
			else:
				peer.send_msg ('For more information please send help or ?\nCommands is not case-sensitive.')
				peer.send_msg (msg.src)
				return;
			
def print_path(success, filename):
	print(filename)	

def on_secret_chat_update(peer, types):
	return "on_secret_chat_update"

def on_user_update(peer, what_changed):
	pass

def on_chat_update(peer, what_changed):
	pass	

# Set callbacks
tgl.set_on_binlog_replay_end(on_binlog_replay_end)
tgl.set_on_get_difference_end(on_get_difference_end)
tgl.set_on_our_id(on_our_id)	
tgl.set_on_secret_chat_update(on_secret_chat_update)
tgl.set_on_user_update(on_user_update)
tgl.set_on_chat_update(on_chat_update)	
tgl.set_on_msg_receive(on_msg_receive)
