import time

class Reduced(object):
    def __init__(self, itm):
        self._itm = itm

    def deref(self):
        return self._itm

def reduced(x):
    return Reduced(x)

def is_reduced(x):
    return isinstance(x, Reduced)

def transduce(xform, rfn, lst):
    f = xform(rfn)
    acc = f()
    for item in lst:
        acc = f(acc, item)
        if is_reduced(acc):
            return f(acc)
    return f(acc)


data = list(range(1024))
dataf = list(map(float, range(1024)))

def map(f):
    def xform_fn(xf):
        def map_rfn(*args):
            l = len(args)
            if l == 0:
                return xf()
            if l == 1:
                return xf(args[0])
            if l == 2:
                return xf(args[0], f(args[1]))
        return map_rfn
    return xform_fn

def filter(f):
    def xform_fn(xf):
        def map_rfn(*args):
            l = len(args)
            if l == 0:
                return xf()
            if l == 1:
                return xf(args[0])
            if l == 2:
                if f(args[1]):
                    return xf(args[0], args[1])
        return map_rfn
    return xform_fn


def inc(x):
    return x + 1

def add(*args):
    l = len(args)
    if l == 0:
        return 0
    if l == 1:
        return args[0]
    if l == 2:
        return args[0] + args[1]

for x in range(1000):
    t = time.time()
    #for x in range(1024):
    #    transduce(map(inc), add, data)
    #print (time.time() - t) * 1000

    t = time.time()
    for x in range(1024):
        transduce(map(inc), add, dataf)
    print (time.time() - t) * 1000