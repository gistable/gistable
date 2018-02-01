#!/usr/bin/python

import time

def new_d():
    return {
        1: 2, 3: 4, 5: 6, 7: 8, 9: 10,
        11: 12, 13: 14, 15: 16, 17: 18, 19: 20
    }

def time_func(iterations, f, *args):
    start = time.time()
    for i in xrange(iterations):
        f(*args)
    return time.time() - start

def try_del(key):
    d = new_d()
    try:
        del d[key]
    except KeyError:
        pass

def if_del(key):
    d = new_d()
    if key in d:
        del d[key]

def pop_del(key):
    d = new_d()
    d.pop(key, None)

def succeed(f):
    f(3)

def fail(f):
    f(4)

iterations = 1000000
print "pop succeed:", time_func(iterations, succeed, pop_del)
print "pop fail:", time_func(iterations, fail, pop_del)
print "try succeed:", time_func(iterations, succeed, try_del)
print "try fail:", time_func(iterations, fail, try_del)
print "if succeed:", time_func(iterations, succeed, if_del)
print "if fail:", time_func(iterations, fail, if_del)