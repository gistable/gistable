#!/usr/bin/env python
"""
Copyright (c) 2011, Daniel Bugl
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by Daniel Bugl.
4. Neither the name of Daniel Bugl nor the names
   of its other contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Daniel Bugl ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import time
import socket

def getInput():
	motd = raw_input('MOTD: ')
	host = raw_input('IP Address: ')
	while True:
		try:
			port = int(raw_input('Port: '))
		except TypeError:
			print 'Error: Invalid port number.'
			continue
		else:
			if (port < 1) or (port > 65535):
				print 'Error: Invalid port number.'
				continue
			else:
				return (host, port, motd)

def writeLog(client, data=''):
	separator = '='*50
	fopen = open('./honey.mmh', 'a')
	fopen.write('Time: %s\nIP: %s\nPort: %d\nData: %s\n%s\n\n'%(time.ctime(), client[0], client[1], data, separator))
	fopen.close()

def main(host, port, motd):
	print 'Starting honeypot!'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	s.listen(100)
	while True:
		(insock, address) = s.accept()
		print 'Connection from: %s:%d' % (address[0], address[1])
		try:
			insock.send('%s\n'%(motd))
			data = insock.recv(1024)
			insock.close()
		except socket.error, e:
			writeLog(address)
		else:
			writeLog(address, data)
        
if __name__=='__main__':
	try:
		stuff = getInput()
		main(stuff[0], stuff[1], stuff[2])
	except KeyboardInterrupt:
		print 'Bye!'
		exit(0)
	except BaseException, e:
		print 'Error: %s' % (e)
		exit(1)