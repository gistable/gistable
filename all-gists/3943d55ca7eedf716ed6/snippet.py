import time
from concurrent.futures import ProcessPoolExecutor
from tornado.ioloop import IOLoop
from tornado import gen

def f(a, b, c, blah=None):
    print "got %s %s %s and %s" % (a, b, c, blah)
    time.sleep(5)
    return "hey there"

@gen.coroutine
def test_it():
    pool = ProcessPoolExecutor(max_workers=1)
    fut = pool.submit(f, 1, 2, 3, blah="ok")  # This returns a concurrent.futures.Future
    print("running it asynchronously")
    ret = yield fut
    print("it returned %s" % ret)
    pool.shutdown()

IOLoop.instance().run_sync(test_it)