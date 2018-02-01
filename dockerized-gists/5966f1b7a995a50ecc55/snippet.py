import random
import time
from tornado import gen
from tornado.concurrent import run_on_executor, futures
from tornado.ioloop import IOLoop

class TaskRunner(object):
    def __init__(self, loop=None):
        self.executor = futures.ThreadPoolExecutor(4)
        self.loop = loop or IOLoop.instance()
        
    @run_on_executor
    def long_running_task(self):
        tau = random.randint(0, 3)
        time.sleep(tau)
        return tau

loop = IOLoop() # this is necessary if running as an ipynb!
tasks = TaskRunner(loop)

@gen.coroutine
def do_stuff():
    result = yield tasks.long_running_task()
    raise gen.Return(result)
        
def do_other_stuff():
    print(random.random())

@gen.coroutine
def main():
    for i in range(10):
        stuff = yield do_stuff()
        print(stuff)
        do_other_stuff()
        
loop.run_sync(main)
