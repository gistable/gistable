# coding=utf8

# Copyright (C) 2011 Saúl Ibarra Corretgé <saghul@gmail.com>
#

import hashlib
import os
import re
import socket
import struct
import Queue

import zmq

from collections import namedtuple
from threading import Event, Thread


READ_ONLY = zmq.POLLIN | zmq.POLLERR
READ_WRITE = READ_ONLY | zmq.POLLOUT

class WSServerSocket(object):
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0)

    def bind(self):
        self._socket.bind((self._ip, self._port))
        self._socket.listen(5)

    def accept(self):
        return self._socket.accept()

    def fileno(self):
        return self._socket.fileno()

    def close(self):
        self._socket.close()


class WSClientSocket(object):
    _digit_re = re.compile(r'[^0-9]')
    _spaces_re = re.compile(r'\s')
    _req_line_re = re.compile('^GET (?P<handler>.*) .*\\r\\n')
    _handshake = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "WebSocket-Origin: %(origin)s\r\n"
        "WebSocket-Location: ws://%(address)s:%(port)s%(handler)s\r\n"
        "Sec-Websocket-Origin: %(origin)s\r\n"
        "Sec-Websocket-Location: ws://%(address)s:%(port)s%(handler)s\r\n"
        "\r\n"
    )
    def __init__(self, sock, handler):
        self._socket = sock
        self._socket.setblocking(0)
        self.handler = handler
        self.handshaken = False
        self.write_queue = Queue.Queue()
        self.headers = ''
        self.data = ''

    def send(self, data):
        self._socket.send(data)

    def recv(self, bufsize):
        return self._socket.recv(bufsize)

    def fileno(self):
        return self._socket.fileno()

    def close(self):
        self._socket.close()

    def _queue_send(self, data):
        try:
            self.write_queue.put_nowait(data)
        except Queue.Full:
            pass

    def queue_send(self, data):
        self._queue_send('\x00%s\xff' % data)

    def data_received(self, data):
        if not self.handshaken:
            if data.startswith('GET'):
                match = self._req_line_re.match(data)
                if not (match and match.groupdict()['handler'] == self.handler):
                    self.close()
                    return
            self.headers += data
            if self.headers.find('\r\n\r\n') != -1:
                parts = self.headers.split('\r\n\r\n', 1)
                self.headers = parts[0]
                if self.do_handshake(self.headers, parts[1]):
                    self.handshaken = True
        else:
            self.data += data
            msgs = self.data.split('\xff')
            self.data = msgs.pop()
            for msg in msgs:
                if msg[0] == '\x00':
                    self.message_received(msg[1:])

    def do_handshake(self, header, key=None):
        part_1 = part_2 = origin = None
        for line in header.split('\r\n')[1:]:
            name, value = line.split(': ', 1)
            if name.lower() == "sec-websocket-key1":
                key_number_1 = int(self._digit_re.sub('', value))
                spaces_1 = len(self._spaces_re.findall(value))
                if spaces_1 == 0:
                    return False
                if key_number_1 % spaces_1 != 0:
                    return False
                part_1 = key_number_1 / spaces_1
            elif name.lower() == "sec-websocket-key2":
                key_number_2 = int(self._digit_re.sub('', value))
                spaces_2 = len(self._spaces_re.findall(value))
                if spaces_2 == 0:
                    return False
                if key_number_2 % spaces_2 != 0:
                    return False
                part_2 = key_number_2 / spaces_2
            elif name.lower() == "host":
                host, _ = value.split(':', 1)
            elif name.lower() == "origin":
                origin = value
        server_ip, server_port = self._socket.getsockname()
        if part_1 and part_2:
            challenge = struct.pack('!I', part_1) + struct.pack('!I', part_2) + key
            response = hashlib.md5(challenge).digest()
            handshake = self._handshake % {
                'origin': origin,
                'address': host,
                'port': server_port,
                'handler': self.handler
            }
            handshake += response
        else:
            # Not using challenge-response
            handshake = self._handshake % {
                'origin': origin,
                'address': host,
                'port': server_port,
                'handler': self.handler
            }
        self._queue_send(handshake)    # Note the _ !
        return True

    def message_received(self, data):
        pass


class ZWSGateway(Thread):

    def __init__(self, config):
        self.config = config
        # setup zeromq socket
        self._poller = zmq.Poller()
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.setsockopt(zmq.SUBSCRIBE, '')      # subscribe to anything
        self._poller.register(self._socket, READ_ONLY)
        # setup websocket server
        self._wsserver = WSServerSocket(str(config.websocket_address), config.websocket_port)
        self._poller.register(self._wsserver, READ_ONLY)
        # mapping: fileno -> socket
        self.fd_map = { self._socket: self._socket,    # zmq sockets don't have fileno()
                        self._wsserver.fileno(): self._wsserver }
        # create a new pipe used for thread termination
        self._pipe = os.pipe()
        self._poller.register(self._pipe[0], zmq.POLLIN)
        self._stop_event = Event()
        Thread.__init__(self)
        self.daemon = True

    def start(self):
        if self.config.use_multicast:
            self._socket.connect('epgm://%s:%d' % (self.config.listen_address, self.config.listen_port))
        else:
            self._socket.bind('tcp://%s:%d' % (self.config.listen_address, self.config.listen_port))
        self._wsserver.bind()
        Thread.start(self)

    def stop(self):
        self._stop_event.set()
        os.write(self._pipe[1], 'stop')
        Thread.join(self)
        self._poller.unregister(self._pipe[0])
        os.close(self._pipe[0])
        os.close(self._pipe[1])
        self._poller.unregister(self._socket)
        self._socket.close()
        self._poller.unregister(self._wsserver)
        self._wsserver.close()

    def run(self):
        while not self._stop_event.is_set():
            events = self._poller.poll()
            for fd, flag in events:
                if fd == self._pipe[0]:
                    # Stop requested
                    for wsclient in (wsclient for wsclient in self.fd_map.values() if wsclient not in (self._socket, self._wsserver)):
                        self._poller.unregister(wsclient)
                        wsclient.close()
                    self.fd_map = {}
                    break
                socket = self.fd_map[fd]
                if flag & zmq.POLLIN:
                    # Ready to read
                    if socket is self._socket:
                        data = self._socket.recv()
                        self.websocket_broadcast(data)
                    elif socket is self._wsserver:
                        sock, addr = socket.accept()
                        wsclient = WSClientSocket(sock, self.config.websocket_handler)
                        self.fd_map[wsclient.fileno()] = wsclient
                        self._poller.register(wsclient, READ_WRITE)
                    else:
                        # Data coming from a WebSocket
                        data = socket.recv(1024)
                        if data:
                            socket.data_received(data)
                        else:
                            self.fd_map.pop(fd)
                            self._poller.unregister(socket)
                            socket.close()
                elif flag & zmq.POLLOUT:
                    # Ready to send
                    if isinstance(socket, WSClientSocket):
                        try:
                            data = socket.write_queue.get_nowait()
                        except Queue.Empty:
                            pass
                        else:
                            socket.send(data)
                elif flag & zmq.POLLERR:
                    # Error
                    self.fd_map.pop(fd)
                    self._poller.unregister(socket)
                    socket.close()

    def websocket_broadcast(self, msg):
        [wsclient.queue_send(msg) for wsclient in (wsclient for wsclient in self.fd_map.values() if wsclient not in (self._socket, self._wsserver))]


Config = namedtuple('Config', ['listen_address', 'listen_port', 'use_multicast', 'websocket_address', 'websocket_port', 'websocket_handler'])

if __name__ == '__main__':
    config = Config('239.192.1.1', 5000, True, '', 9999, '/test')
    server = ZWSGateway(config)
    server.start()
    while True:
        try:
            c = raw_input('> ')
            if c == 'quit':
                break
        except KeyboardInterrupt:
            break
    server.stop()

