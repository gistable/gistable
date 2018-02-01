from threadpool import ThreadPool
import random
import gevent
import gevent.pool

iterations = 1000000
max_stack_depth = 50

def source(tp):
    for i in xrange(0, iterations):
        i = tp.apply(threaded, i)
        if i % 10000 == 0:
            print i

def recurse(x, y, z, remaining):
    if remaining:
        return recurse(x, y, z, remaining - 1)
    return 0

def threaded(i):
    recurse(1, 2, 3, random.randint(0, max_stack_depth))
    return i

tp = ThreadPool(poolsize=100)
p1 = gevent.pool.Pool(size=1)
p1.spawn(source, tp)
p1.join()
