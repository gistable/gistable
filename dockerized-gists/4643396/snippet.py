#!/usr/bin/env python

"""
How to use it:
1. Just `kill -2 PROCESS_ID` or `kill -15 PROCESS_ID` , The Tornado Web Server Will shutdown after process all the request.
2. When you run it behind Nginx, it can graceful reboot your production server.

3. Nice Print in http://weibo.com/1682780325/zgkb7g8k7

"""

import time
import signal
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def shutdown():
    logging.info('Stopping http server')
    server.stop()

    logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info('Shutdown')
    stop_loop()


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    
    global server

    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    tornado.ioloop.IOLoop.instance().start()

    logging.info("Exit...")


if __name__ == "__main__":
    main()