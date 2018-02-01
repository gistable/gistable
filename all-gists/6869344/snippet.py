#!/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

import time

from tornado.options import define, options
define("port", default=7000, help="run on the given port", type=int)

class SleepHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(10)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        start = time.time()
        res = yield self.sleep()
        self.write("when i sleep %f s" % (time.time() - start))
        self.finish()

    @run_on_executor
    def sleep(self):
        time.sleep(5)
        return 5

class JustNowHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("i hope just now see you")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
            (r"/sleep", SleepHandler), (r"/justnow", JustNowHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()