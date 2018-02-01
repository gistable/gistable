# -*- coding: utf-8 -*-
"""Simple echo server for educational purposes.

Based directly on python interface to Linux epoll mechanism. 
Uses greenlets.
"""
import socket
import select
import errno
from greenlet import greenlet
from functools import partial

TERM = '\n'

def init_server_socket(host='localhost', port=8080):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.setblocking(0)
    ss.bind(('localhost', 8080))
    ss.listen(1)
    return ss


class Server(object):
    """ """
    def __init__(self, app):
        self.app = app
        self.server_socket = init_server_socket()
        self.epoll = select.epoll()
        self.streams = {}
        self.epoll.register(self.server_socket.fileno(), select.EPOLLIN)

    def _handle_accept(self):
        """ """
        conn, addr = self.server_socket.accept()
        conn.setblocking(0)
        print "peer has opened connection, fileno: {0} ".format(conn.fileno())
        self.epoll.register(conn.fileno(), select.EPOLLIN)
        # each connection is associated with a greenlet
        # that keeps connection io-state.
        self.streams[conn.fileno()] = greenlet(partial(self._stream_greenlet, conn=conn))

    def _handle_io(self, fd):
        """ """
        self.streams[fd].switch()
        
    def _handle_hup(self, fd):
        """ """
        self.streams[fd].throw()

    def _loop(self):
        try:
            while True:
                events = self.epoll.poll(1)
                for fd, evt in events:
                    if fd == self.server_socket.fileno():
                        self._handle_accept()
                    # It important that EPOLLHUP goes before EPOLLIN.
                    # Otherwise _handle_hup is never reached because 
                    # EPOLLHUP occures not alone but in conjunction
                    # with EPOLLIN or EPOLLOUT. 
                    elif evt & select.EPOLLHUP:
                        self._handle_hup(fd)
                    elif evt & select.EPOLLIN or evt & select.EPOLLOUT:
                        self._handle_io(fd)
        finally:
            self.shutdown()

    def _stream_greenlet(self, conn):
        try:
            this = greenlet.getcurrent()
            req = ""
            while True:
                req_ready, req = self._read_request(conn, req)
                # tell epoll to monitor whether the socket is writable
                self.epoll.modify(conn.fileno(), select.EPOLLOUT)
                this.parent.switch()
                self._write_response(conn, self.app(req_ready))
                # tell epoll to monitor whether the socket is readable
                self.epoll.modify(conn.fileno(), select.EPOLLIN)
                this.parent.switch()
        except greenlet.GreenletExit:
            self._close_connection(conn)

    def _read_request(self, conn, request):
        req = request
        while True:
            req += conn.recv(1024)
            terminal_index = req.find(TERM)
            if terminal_index:
                return req[:terminal_index], req[terminal_index + 1:]
            else:
                this.parent().switch()

    def _write_response(self, conn, resp):
        while True:
            try:
                bytes_written = conn.send(resp)
            except socket.error as e:
                # in case when peer closes connection
                if e.errno == errno.EPIPE:
                    raise greenlet.GreenletExit
                else:
                    raise e
            else:
                resp = resp[bytes_written:]
                if resp:
                    this.parent.switch()
                else:
                    return

    def _close_connection(self, conn):
        print "peer has closed connection, fileno: {0} ".format(conn.fileno())
        fd = conn.fileno()
        self.epoll.unregister(fd)
        conn.close()
        del self.streams[fd]

    def start(self):
        self._loop()

    def shutdown(self):
        self.epoll.unregister(self.server_socket.fileno())
        self.epoll.close()
        self.server_socket.close()


if __name__ == "__main__":
    def application(request):
        return ">>> {}:{}\n".format(request, len(request))
    
    server = Server(app=application)
    server.start()
