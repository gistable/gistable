#!/usr/bin/env python
# Thread pool based on: http://code.activestate.com/recipes/577187-python-thread-pool/

from queue import Queue
from threading import Thread
from functools import partial

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import gen
from tornado.ioloop import IOLoop

import himitsu


def make_hash(text):
    b = himitsu.Bcrypt()
    return b.encode(text)


class WorkerThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kwargs, callback = self.queue.get()
            try:
                result = func(*args, **kwargs)
                if callback is not None:
                    IOLoop.instance().add_callback(partial(callback, result))
            except Exception as e:
                print(e)
            self.queue.task_done()


class ThreadPool(object):
    def __init__(self, num_threads):
        self.queue = Queue()
        for _ in range(num_threads):
            WorkerThread(self.queue)

    def add_task(self, func, args=(), kwargs={}, callback=None):
        self.queue.put((func, args, kwargs, callback))

    def wait_completion(self):
        self.queue.join()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def pool(self):
        if not hasattr(self.application, 'pool'):
            self.application.pool = ThreadPool(20)
        return self.application.pool


class IndexHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        result = yield gen.Task(
            self.pool.add_task, make_hash, ('Test',)
        )
        self.write(result)
        self.finish()

def main():
    try:
        tornado.options.parse_command_line()

        application = tornado.web.Application([
            (r'/', IndexHandler)
        ], debug=True)

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('Exit')


if __name__ == '__main__':
    main()
