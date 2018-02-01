#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import socket


class ProxyHandler(object):
    def __init__(self, request):
        self._request = request
        addr = request.host.split(':')
        if len(addr) > 0:
            addr[1] = int(addr[1])
        else:
            addr.append(80)
        addr = tuple(addr)
        message = "You requested %s\n" % request.uri
        remote_stream = tornado.iostream.IOStream(socket.socket())
        self._remote_stream = remote_stream
        self._local_stream = request.connection.stream
        remote_stream.connect(addr, self._on_connect)
        # request.finish()

    def _on_connect(self):
        self._local_stream.write('HTTP/1.0 200 Connection established\r\nProxy-agent: proxy.py/1.0\r\nConnection: Close\r\n\r\n')
        self._local_stream.read_until_close(self._on_local_close, self._on_local)
        self._remote_stream.read_until_close(self._on_remote_close, self._on_remote)

    def _on_remote_close(self, data):
        self._request.finish()

    def _on_local_close(self, data):
        self._remote_stream.close()

    def _on_remote(self, data):
        self._local_stream.write(data)

    def _on_local(self, data):
        self._remote_stream.write(data)


http_server = tornado.httpserver.HTTPServer(ProxyHandler)
http_server.listen(8888)
tornado.ioloop.IOLoop.instance().start()
