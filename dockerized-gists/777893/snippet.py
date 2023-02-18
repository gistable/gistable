#
# "THE BEER-WARE LICENSE":
# <truemped at goggle.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Daniel Truemper
#

import time

import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream

from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class Downloader(object):

    def __init__(self, in_socket, out_socket, io_loop):
        self._in_socket = in_socket
        self._in_socket.setsockopt(zmq.HWM, 10)
        self._out_socket = out_socket
        self._io_loop = io_loop
        self._client = AsyncHTTPClient(self._io_loop,
            max_clients=10, max_simultaneous_connections=1)

        self._stream = ZMQStream(self._in_socket, self._io_loop)
        self._stream.on_recv(self._receive)

    def _receive(self, msg):
        """
        Msg is a URL we should download or 'EXIT'.
        """
        if msg[0] == "EXIT":
            print "stopping downloader"
            self._stream.flush()
            self._stream.stop_on_recv()
            self._out_socket.send_unicode(msg[0])
        else:
            self._download_this(msg)

    def _download_this(self, url):
        print url[0]
        req = HTTPRequest(url[0].encode("utf-8"))
        self._client.fetch(req, self._handle_response)
        
    def _handle_response(self, response):
        if response.error:
            print "Error: %s", response.error
        else:
            # simply send the response body to the ougoing ZMQ socket
            self._out_socket.send_multipart([response.request.url,
                str(response.request_time)])


def main(urls):
    ctx = zmq.Context(1)
    io_loop = ioloop.IOLoop.instance()
    
    main_push = ctx.socket(zmq.PUSH)
    main_push.bind('inproc://main/download')

    worker_pull = ctx.socket(zmq.PULL)
    worker_pull.connect('inproc://main/download')

    worker_pub = ctx.socket(zmq.PUB)
    worker_pub.bind('inproc://worker/fetched')

    main_sub = ctx.socket(zmq.SUB)
    main_sub.connect('inproc://worker/fetched')
    main_sub.setsockopt(zmq.SUBSCRIBE, "")

    def print_and_send_2_more(msg):
        if len(msg) == 2:
            print "Downloading of %s took %s'" % (msg[0], msg[1])
        else:
            print "should exit"
            ioloop.DelayedCallback(io_loop.stop, 5000.0, io_loop).start()

    main_stream = ZMQStream(main_sub, io_loop)
    main_stream.on_recv(print_and_send_2_more)

    downloader = Downloader(worker_pull, worker_pub, io_loop)

    for url in urls:
        main_push.send_unicode(url)

    print "starting"
    io_loop.start()
    print "finished"

    main_push.close()
    main_sub.close()
    worker_pull.close()
    worker_pub.close
    ctx.term()


if __name__ == '__main__':
    urls = [
        u'http://www.google.com',
        u'http://www.yahoo.com',
        u'http://www.microsoft.com',
        u'EXIT'
    ]
    main(urls)