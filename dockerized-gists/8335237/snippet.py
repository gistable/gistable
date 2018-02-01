# -*- coding: utf-8
from time import sleep, time
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, asynchronous, RequestHandler
from multiprocessing.pool import ThreadPool
from tornado import gen
 
 
pool = ThreadPool(10)
 
 
def run_background(func, callback, args=(), kwargs={}):
    def _callback(result):
        IOLoop.instance().add_callback(lambda: callback(result))
    pool.apply_async(func, args, kwargs, _callback)
 
 
def blocking_task(n):
    sleep(n)
    return n
 
 
class Handler(RequestHandler):
    @asynchronous
    @gen.engine
    def get(self):
        t = time()
        res = yield gen.Task(run_background, blocking_task, args=(10, ))
        self.write("Started at {} got {}".format(t, res))
        self.finish()
 
 
class AHandler(RequestHandler):
    @asynchronous
    def get(self):
        self.write("Test {0}".format(time()))
        self.finish()
 
 
HTTPServer(Application([
    ("/", Handler),
    ("/a", AHandler)
    ], debug=True)).listen(9999)
IOLoop.instance().start()