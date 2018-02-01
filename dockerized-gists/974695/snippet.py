import errno
import functools
import socket
from tornado import ioloop, iostream


class Connection(object):
    def __init__(self, connection):
        self.stream = iostream.IOStream(connection)
        self._read()

    def _read(self):
        self.stream.read_until('\r\n', self._eol_callback)

    def _eol_callback(self, data):
        self.handle_data(data)


def connection_ready(sock, fd, events):
    while True:
        try:
            connection, address = sock.accept()
        except socket.error, e:
            if e[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        else:
            connection.setblocking(0)
            CommunicationHandler(connection)


class CommunicationHandler(Connection):
    """Put your app logic here"""
    def handle_data(self, data):
        self.stream.write(data)
        self._read()


if __name__ == '__main__':
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(("", 8000))
    sock.listen(128)

    io_loop = ioloop.IOLoop.instance()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    
    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
        print "exited cleanly"
