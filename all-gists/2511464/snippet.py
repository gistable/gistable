'''
Created on Apr 27, 2012

Based on echo server http://tornadogists.org/1231481/ by phus

@author: mark-allen
'''

import logging

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.netutil import TCPServer

class ChatConnection(object):
	
	def __init__(self, stream, address, connections):
		logging.info('receive a new connection from %s', address)
		self.state = 'AUTH'
		self.name = None
		self.connections = connections;
		self.stream = stream
		self.address = address
		self.stream.set_close_callback(self._on_close)
		self.stream.read_until('\n', self._on_read_line)
		stream.write('Enter your name: ', self._on_write_complete)
	
	def _on_read_line(self, data):
		logging.info('read a new line from %s', self.address)
		if self.state == 'AUTH':
			name = data.rstrip();
			if self.connections.has_key(name):
				self.stream.write('Name taken, choose another: ', self._on_write_complete)
				return
			# message = 'Welcome, %s!\n' % (name)
			self.stream.write('Welcome, %s!\n' % (name), self._on_write_complete)
			self.connections[name] = self
			self.name = name
			self.state = 'CHAT'
			message = '%s has arrived\n' % (self.name)
			for _,conn in self.connections.iteritems():
				if conn != self:
					conn.stream.write(message, self._on_write_complete)
		else:
			message = '<%s> %s\n' % (self.name, data.rstrip())
			for _,conn in self.connections.iteritems():
				if conn != self:
					conn.stream.write(message, self._on_write_complete)
	
	def _on_write_complete(self):
		logging.info('wrote a line to %s', self.address)
		if not self.stream.reading():
			self.stream.read_until('\n', self._on_read_line)
	
	def _on_close(self):
		logging.info('client quit %s', self.address)
		if self.name != None:
			del self.connections[self.name]
			message = '%s has left\n' % (self.name)
			for _,conn in self.connections.iteritems():
				conn.stream.write(message, self._on_write_complete)

class ChatServer(TCPServer):

	def __init__(self, io_loop=None, ssl_options=None, **kwargs):
		logging.info('a echo tcp server is started')
		TCPServer.__init__(self, io_loop=io_loop, ssl_options=ssl_options, **kwargs)

	def handle_stream(self, stream, address):
		ChatConnection(stream, address, chat_connections)

def main(connections):
	chat_server = ChatServer()
	chat_server.listen(8888)
	IOLoop.instance().start()

chat_connections = {}

if __name__ == '__main__':
	main(chat_connections)
