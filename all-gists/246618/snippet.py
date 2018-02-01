import logging
import random

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        import tornado.ioloop
        self.scheduler = tornado.ioloop.PeriodicCallback(self._check, 1e3)
        self.scheduler.start()

    def _check(self):
        if self._are_where_there_yet():
            self.scheduler.stop()
            self.write("Hello, world")
            self.finish()

    def _are_where_there_yet(self):
        n = random.randint(1,10)
        logging.info("current value: %s", n)
        return n == 5


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()