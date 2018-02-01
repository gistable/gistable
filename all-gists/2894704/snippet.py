import functools
import time
import threading
import logging
import Queue
import hunspell

import tornado.web
import tornado.websocket
import tornado.locale
import tornado.ioloop
from tornado.options import define, options

define('debug', type=bool, default=False, help='run in debug mode with autoreload (default: false)')

class Handler(tornado.web.RequestHandler):
    @property
    def queue(self):
        return self.application.queue

    @tornado.web.asynchronous
    def get(self, word):
        self.queue.put( (word, self.on_callback) )

    def on_callback(self, output):
        self.write("Thread output: %s" % output)
        self.finish()

class ThreadWord(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.hobj = hunspell.HunSpell('./fr-classique.dic', './fr-classique.aff')

    def run(self):
        while True:
            try:
                word, callback = self.queue.get(True, 1)
            except Queue.Empty:
                continue
            # cpu intensive work ...
            output = self.hobj.spell(word)
            tornado.ioloop.IOLoop.instance().add_callback(functools.partial(callback, output))
            self.queue.task_done()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/(.*)", Handler),
        ]
        settings = {
            'cookie_secret': 'W/wT5ndaR/2sa3m8OOQ5q0xDvnZclE4BtimO1f+QM2Y=',
            'debug':options.debug,
        }
        tornado.web.Application.__init__(self, handlers, **settings)

        self.queue = Queue.Queue()

        for i in range(5):
            t = ThreadWord(self.queue)
            t.setDaemon(True)
            t.start()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application = Application()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
