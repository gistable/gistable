# source: https://bitbucket.org/Zaeyx/rubberglue

import socket,asyncore
import time
import random
import hashlib
import os

class core():
	def __init__(self, logfile, syslog=False, cap=False):
		self.logfile = logfile
		self.cap = cap
		fi = open(self.logfile, 'a')
		fi.close()
		if not os.path.exists("./capture"):
			os.makedirs("./capture")
		
	def logg(self, msg):
		fi = open(self.logfile, "a")
		fi.write(time.strftime("%H:%M:%S %m/%d/%Y") + "; " + msg + "\n")
		fi.close()
	
	def make_hash(self, data):
		return hashlib.sha1(str(data)).hexdigest()

	def capture(self, tag, data):
		if not self.cap == False:
			fi = open(r"capture/" + str(tag), "a")
			fi.write(str(data))
			fi.close()

class forwarder(asyncore.dispatcher):
	def __init__(self, ip, port, backlog=5):
		asyncore.dispatcher.__init__(self)
		self.remoteport=port
		self.port = port
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((ip,port))
		self.listen(backlog)

	def handle_accept(self):
		conn, addr = self.accept()
		tag = instance.make_hash(time.strftime("%H:%M:%S %m/%d/%Y") + str(addr) + str(self.port))
		print "Connection from: "+addr[0]+":"+str(addr[1])+"->"+str(self.port)
		instance.logg("Connection from: " + addr[0] + ":" + str(addr[1]) + "->" + str(self.port) +"; "+ tag)
		sender(receiver(conn, tag),addr[0],self.remoteport, tag)

class receiver(asyncore.dispatcher):
	def __init__(self,conn, tag):
		self.tag = tag
		asyncore.dispatcher.__init__(self,conn)
		self.from_remote_buffer=''
		self.to_remote_buffer=''
		self.sender=None

	def handle_connect(self):
		pass

	def handle_read(self):
		read = self.recv(4096)
		self.from_remote_buffer += read
		if not read == None:
			instance.capture(self.tag, read)

	def writable(self):
		return (len(self.to_remote_buffer) > 0)

	def handle_write(self):
		sent = self.send(self.to_remote_buffer)
		self.to_remote_buffer = self.to_remote_buffer[sent:]

	def handle_close(self):
		self.close()
		if self.sender:
			self.sender.close()

class sender(asyncore.dispatcher):
	def __init__(self, receiver, remoteaddr, remoteport, tag):
		asyncore.dispatcher.__init__(self)
		self.receiver=receiver
		self.tag = tag
		receiver.sender=self
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((remoteaddr, remoteport))

	def handle_connect(self):
		pass

	def handle_read(self):
		read = self.recv(4096)
		self.receiver.to_remote_buffer += read
		if not read == None:
			instance.capture(self.tag, str(read))

	def writable(self):
		return (len(self.receiver.from_remote_buffer) > 0)

	def handle_write(self):
		sent = self.send(self.receiver.from_remote_buffer)
		self.receiver.from_remote_buffer = self.receiver.from_remote_buffer[sent:]

	def handle_close(self):
		self.close()
		self.receiver.close()

if __name__ == "__main__":
	import sys

	if len(sys.argv) < 2:
		print "You need to give a port"
		print "Usage: ", sys.argv[0], " <port>"
		sys.exit(1)

	local_ip = ''
	#remote_ip = '127.0.0.1'
	remote_port = 1337
	local_port = int(sys.argv[1])
	instance = core("log.txt")
	
	for i in range(len(sys.argv) - 1):
		forwarder(local_ip,int(sys.argv[i+1]))
	asyncore.loop()