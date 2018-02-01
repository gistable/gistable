#
# This piece of code is written by
#    Jianing Yang <jianingy.yang@gmail.com>
# with love and passion!
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#                             27 Apr, 2016
#
from collections import deque
from tornado import ioloop
from tornado import stack_context
from tornado.concurrent import TracebackFuture
from tornado.gen import coroutine
from tornado.log import gen_log

import errno
import socket

class IODatagram(object):

    def __init__(self, sock, io_loop=None):
        self.io_loop = io_loop or ioloop.IOLoop.current()
        self.socket = sock
        self._state = None
        # TODO: max size should be 65535 for IPv6 jumbograms
        self.max_write_chunk_size = 65507
        self.max_read_chunk_size = 65507
        self.read_chunk_size = self.max_read_chunk_size
        self._read_callback = None
        self._read_future = None
        self._write_buffer = deque()
        self._write_callback = None
        self._write_future = None

        self.socket.setblocking(0)

    def _add_io_state(self, state):
        if self._state is None:
            self._state = ioloop.IOLoop.ERROR | state
            self.io_loop.add_handler(
                self.fileno(), self._handle_events, self._state)
        elif not self._state & state:
            self._state = self._state | state
            self.io_loop.update_handler(self.fileno(), self._state)

    def _handle_events(self, fd, events):
        try:
            if events & self.io_loop.READ:
                self._handle_read()
            if events & self.io_loop.WRITE:
                self._handle_write()
            if events & self.io_loop.ERROR:
                self.error = self.get_fd_error()
                return
            state = self.io_loop.ERROR
            if self.reading():
                state |= self.io_loop.READ
            if self.writing():
                state |= self.io_loop.WRITE
            if state != self._state:
                assert self._state is not None, \
                    "shouldn't happen: _handle_events without self._state"
                self._state = state
                self.io_loop.update_handler(self.fileno(), self._state)
        except Exception:
            raise

    def fileno(self):
        return self.socket.fileno()

    def reading(self):
        return False

    def _handle_read(self):
        chunk, address = self.read_from_fd()
        if chunk is None:
            return
        if self._read_callback:
            callback = self._read_callback
            self._read_callback = None
            callback(chunk, address)
        if self._read_future:
            future = self._read_future
            self._read_future = None
            future.set_result((chunk, address))


    def _handle_write(self):
        while self._write_buffer:
            try:
                data, address = self._write_buffer[0]
                num_bytes = self.write_to_fd(data, address)
                self._write_buffer.popleft()
                if num_bytes < len(data):
                    self._write_buffer.appendleft((data[num_bytes], address))
            except(socket.error, IOError, OSError) as e:
                if e.args[0] in (errno.EAGAIN, errno.EWOULDBLOCK):
                    break
                else:
                    gen_log.warning("Write error on %s: %s", self.fileno(), e)
                    return
        if not self._write_buffer:
            if self._write_callback:
                callback = self._write_callback
                self._write_callback = None
                callback()
            if self._write_future:
                future = self._write_future
                self._write_future = None
                future.set_result(None)

    def bind(self, host, port):
        self.socket.bind((host, port))

    def read_from_fd(self):
        try:
            chunk, address = self.socket.recvfrom(self.read_chunk_size)
        except socket.error as e:
            if e.args[0] in (errno.EAGAIN, errno.EWOULDBLOCK):
                return None, None
            else:
                raise
        if not chunk:
            return None, None
        return chunk, address

    def read(self, callback=None):
        assert not self.reading(), 'Already reading'
        if callback is not None:
            self._read_callback = stack_context.wrap(callback)
            future = None
        else:
            future = self._read_future = TracebackFuture()
            future.add_done_callback(lambda f: f.exception())

        self._add_io_state(self.io_loop.READ)

        return future

    def reading(self):
        return bool(self._read_callback)

    def write(self, data, address, callback=None):
        for i in range(0, len(data), self.max_write_chunk_size):
            payload = (data[i:i + self.max_write_chunk_size], address)
            self._write_buffer.append(payload)
        if callback is not None:
            self._write_callback = stack_context.wrap(callback)
            future = None
        else:
            future = self._write_future = TracebackFuture()
            future.add_done_callback(lambda f: f.exception())
        self._handle_write()
        if self._write_buffer:
            self._add_io_state(self.io_loop.WRITE)
        return future

    def write_to_fd(self, data, address):
        return self.socket.sendto(data, address)

    def writing(self):
        return bool(self._write_buffer)

@coroutine
def main_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c = IODatagram(sock)

    # use as server
    c.bind('0.0.0.0', 11211)
    data, address = yield c.read()
    yield c.write(data, address)

@coroutine
def main_raw():
    from scapy.all import IP, UDP, DNS, DNSQR
    address = ('114.114.114.114', 53)
    r = (IP(dst=address[0], src='127.0.0.1')
         /UDP(dport=address[1], sport=53)
         /DNS(rd=1,qd=DNSQR(qname="www.baidu.com")))
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    c = IODatagram(s)
    yield c.write(bytes(r), address)


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(main_udp)
    ioloop.IOLoop.instance().run_sync(main_raw)
