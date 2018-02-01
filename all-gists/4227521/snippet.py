#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  asterisk.py
#  
#  Copyright 2014 James Finstrom<jfinstrom at gmail>
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
#  
import os
import sys
import socket
import ConfigParser

mgrcnf = '/etc/asterisk/manager.conf'
mgruser = 'admin'

config = ConfigParser.ConfigParser()
config.read(mgrcnf)
username = mgruser
password = config.get( mgrusr, 'secret')
""" Initialize the dictionary in the global space """

def make_dict(lst):
	ret ={}
	for i in lst:
		i = i.strip()
		if i and i[0] is not "#" and i[-1] is not "=":
			var,val = i.rsplit(":",1)
			ret[var.strip()] = val.strip()
	return ret

class acli:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverip = '127.0.0.1'
		self.serverport = 5038
		self.username = ''
		self.password = ''
	def sendCmd(self,action,**args):
		self.sock.send("Action: %s\r\n" % action)
		for key, value in args.items():
			self.sock.send("%s: %s\r\n" % (key,value))
		self.sock.send("\r\n")
		data = []
		while '\r\n\r\n' not in ''.join(data)[-4:]:
			buf = self.sock.recv(1)
			data.append(buf)				
		l = ''.join(data).split('\r\n')
		return l
		
				
	def conn(self):
		self.sock.connect((self.serverip, self.serverport))
		ret = self.sendCmd("login", Username=self.username, Secret=self.password)
		if 'Success' in ret[1]:
			return True
		else:
			return False
def callCalvery(mesg, doing)
	#put your action here
	pass
			
def main():
	ampconf()
	ast = acli()
	ast.username = username
	ast.password = password
	if ast.conn():
		dev = ast.sendCmd('SIPShowPeer', Peer='1000')
		value = make_dict(dev)
		if value['Response'] == 'Success':
			if value['Status'] == 'OK':
				pass
			else:
				callCalvery(value['status'], 'peer 1000')
		else:
			callCalvery(value['Message'], 'api call')
			
	return 0

if __name__ == '__main__':
	main()

