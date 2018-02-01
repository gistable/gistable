#!/usr/bin/env python

from multiprocessing import Process, Queue
import os
import sys
import time
import tornado.ioloop
import tornado.web


class SerializedWorker():
  '''holds a forked process worker and an in memory queue for passing messages'''
  def __init__(self):
    self.q = Queue()
    # for a process with the forked_process function
    self.p = Process(target=self.forked_process, args=(self.q,))
    self.p.start()
    self.counter = 0

  # this function runs out of process
  def forked_process(self, q):
    while True:
      work = q.get()
      try:
        print("Got work: %d in process %d" % (work, os.getpid()))
        time.sleep(1)
        print("Done working on: %d" % work)
      except:
        # would probably want to retry once or twice on exception
        print("Got exception " + sys.exc_info())

  def queue_work(self):
    '''queue some work for the process to handle'''
    self.counter += 1
    # a hash could be pass through for more complex values
    self.q.put(self.counter)


class MainHandler(tornado.web.RequestHandler):
  def initialize(self, worker):
    self.worker = worker

  def get(self):
    self.worker.queue_work()
    self.write("Queued processing of %d\n" % worker.counter)


if __name__ == "__main__":
  worker = SerializedWorker()
  application = tornado.web.Application([
    (r"/", MainHandler, dict(worker=worker)),
  ])
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()