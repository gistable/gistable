""" SocketWrapper is a small wrapper that overrides the recv() function of zmq's
    python object so that it uses poll so it has a default timeout. """
    
import zmq
import socket

class TimeoutError(Exception): pass

class SocketWrapper(object):
    def __init__(self, socket):
        self.socket = socket
    
    def __getattr__(self, item):
        return getattr(self.socket, item)
    
    def recv(self, timeout=10000):
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        msg = dict(poller.poll(timeout))
        if len(msg) > 0:
            return self.socket.recv()
        
        raise TimeoutError()