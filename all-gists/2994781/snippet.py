from eventlet.pools import Pool
from eventlet.timeout import Timeout

class SocketPool(Pool):
    """A pool of sockets connected to a component

    If a socket times out in use, simply close if before handing it back to the
    pool and it will be discarded and a replacement inserted into the pool."""

    def __init__(self, address, **kwargs):
        self.address = address
        super(SocketPool, self).__init__(**kwargs)

    def __str__(self):
        return self.address

    def __repr__(self):
        return "<SocketPool: %s>" % self

    def create(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect(self.address)
        socket.setsockopt(zmq.LINGER, 0)
        return socket

    def put(self, socket):
        """Wrapper around superclass put, replacing socket if closed"""
        if socket.closed:
            socket = self.create()
        super(SocketPool, self).put(socket)


def do_req_rep(destination_pool, message):
    with destination_pool.item() as socket:
        try:
            with Timeout():
                socket.send(message)
                return socket.recv()
        except TimeoutException:
            socket.close()
    
