#!/usr/bin/env python
#TheZero
#This code is under Public Domain

from threading import Thread
import socket
host = raw_input('host > ')
from_port = input('start scan from port > ')
to_port = input('finish scan to port > ')   
counting_open = []
counting_close = []
threads = []

def scan(port):
	s = socket.socket()
	result = s.connect_ex((host,port))
	print('working on port > '+(str(port)))      
	if result == 0:
		counting_open.append(port)
		#print((str(port))+' -> open') 
		s.close()
	else:
		counting_close.append(port)
		#print((str(port))+' -> close') 
		s.close()

for i in range(from_port, to_port+1):
	t = Thread(target=scan, args=(i,))
	threads.append(t)
	t.start()
	
[x.join() for x in threads]

print(counting_open)
	
