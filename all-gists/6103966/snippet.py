import logging
import zmq

class ZmqClient (object):

	def __init__(self, socket, logger):
		super(ZmqClient, self).__init__()

		self._logger = logger
		self._socket = socket
		self._fd = socket.fd
		self._callback = None
		self._reactor = None

	def logPrefix(self): 
		""" Needed by twisted. """
		return '.'.join([self.__class__.__name__, str(self.fileno())])

	def fileno(self):
		""" Needed by twisted. """
		return self._fd

	def __str__(self):
		return self.logPrefix()

	def connectionLost(self, reason):
		""" Needed by twisted. """
		self._logger.info("{} unregistering from {}".format(self, self._reactor))
		self._reactor.removeReader(self)
		self._logger.warning("connection lost: {}".format(reason))

	def onReadable(self, callback):
		self._callback = callback
		return self

	def doRead(self):
		while self._socket.events & zmq.POLLIN: 
			#print "D: {} invoking {} with {}".format(self, self._callback, self._socket)
			self._callback(self._socket)

	def registerOn(self, reactor):
		if not self._callback: raise Exception('callback is not set')

		self._logger.info("{} registered in {}".format(self, reactor))
		self._reactor = reactor
		self._reactor.addReader(self)
		return self


class Dumper:
	def __init__(self, logger):
		self._logger = logger
		
	def __call__(self, socket):
		""" Invoked by Twisted reactor when data is readable on socket. """
		data = socket.recv_multipart()
		self._logger.info("data received: {}".format(data))

		
if __name__ == "__main__":
        ctx = zmq.Context()
        socket = ctx.socket(zmq.SUB)
        socket.bind("tcp://*:5563")
        socket.subscribe = ""

	logging.basicConfig()
        logger = logging.getLogger()

        dumper = Dumper(logger)

        from twisted.internet import reactor
        zmq_client = ZmqClient(socket, logger) \
        		.onReadable(dumper)    \
        		.registerOn(reactor)
        reactor.run()
