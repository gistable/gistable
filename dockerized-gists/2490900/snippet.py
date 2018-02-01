# encoding=utf-8
# Usage: python filename.py
# Background Run: nohup python filename.py 2079 &
# http://yaonie.org/

import socket, thread, select, sys


BUFLEN = 8192
HTTPVER = 'HTTP/1.1'

class ConnectionHandler:
	def __init__(self, connection, address, timeout):
		self.client = connection
		self.client_buffer = ''
		self.timeout = timeout
		self.method, self.path, self.protocol = self.get_base_header()
		if self.method=='CONNECT':
			self.method_CONNECT()
		elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST',):# 'PUT','DELETE', 'TRACE'):
			self.method_others()
		self.client.close()
		self.target.close()

	def get_base_header(self):
		while 1:
			self.client_buffer += self.client.recv(BUFLEN)
			end = self.client_buffer.find('\n')
			if end!=-1:
				break
		print '%s'%self.client_buffer[:end]#debug
		data = (self.client_buffer[:end+1]).split()
		self.client_buffer = self.client_buffer[end+1:]
		return data

	def method_CONNECT(self):
		self._connect_target(self.path)
		self.client.send(HTTPVER+' 200 Connection established\nProxy-agent: %s\n\n') % \
		r"Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)')"
		self.client_buffer = ''
		self._read_write()		

	def method_others(self):
		self.path = self.path[7:]
		i = self.path.find('/')
		host = self.path[:i]		
		path = self.path[i:]
		self._connect_target(host)
		self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+self.client_buffer)
		self.client_buffer = ''
		self._read_write()

	def _connect_target(self, host):
		i = host.find(':')
		if i!=-1:
			port = int(host[i+1:])
			host = host[:i]
		else:
			port = 80
		(soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
		self.target = socket.socket(soc_family)
		self.target.connect(address)

	def _read_write(self):
		time_out_max = self.timeout/3
		socs = [self.client, self.target]
		count = 0
		while 1:
			count += 1
			(recv, _, error) = select.select(socs, [], socs, 3)
			if error:
				break
			if recv:
				for in_ in recv:
					data = in_.recv(BUFLEN)
					if in_ is self.client:
						out = self.target
					else:
						out = self.client
					if data:
						out.send(data)
						count = 0
			if count == time_out_max:
				break

def start_server(host, port, IPv6=False, timeout=60, handler=ConnectionHandler):
	if IPv6==True:
		soc_type=socket.AF_INET6
	else:
		soc_type=socket.AF_INET
	soc = socket.socket(soc_type)
	soc.bind((host, port))
	print "Serving on %s:%d."%(host, port)#debug
	soc.listen(0)
	while 1:
		thread.start_new_thread(handler, soc.accept()+(timeout,))

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'usage: python %s port' % sys.argv[0]
		sys.exit()
	try:
		port = int(sys.argv[1])
	except:
		print 'usage: python %s port' % sys.argv[0]
		sys.exit()
		
	start_server('10.1.14.2',port)
