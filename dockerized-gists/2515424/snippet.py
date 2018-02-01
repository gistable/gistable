# measure time taken to modify and filter a list of numbers using different methods.

# http://stackoverflow.com/questions/1685221/accurately-measure-time-python-function-takes
from __future__ import with_statement
import time
from collections import defaultdict

class Timer(object):
    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type, value, traceback):
        # Error handling here
        self.__finish = time.time()

    def duration_in_seconds(self):
        return self.__finish - self.__start

timer = Timer()

# a huge list
thelist = [x for x in range(10000)]

# list processing funciton
def thefunc(x):
    if x%1000 == 0:
        return None
    return x+x
    


# 1. cycle
def cycle():
    out = []
    for i in thelist:
        o = thefunc(i)
        if o is not None:
            out.append(o)

# 2. comprehensions
def comprehensions():
    [x for x in [thefunc(y) for y in thelist] if x is not None]

# 3. map/filter
def mapfilter():
    filter(lambda x: x is not None,map(thefunc,thelist))
    
# 4. generator
def genfunc():
    for x in thelist:
        r = thefunc(x)
        if r is not None:
            yield r
            
def generator():
    [x for x in genfunc()]


def test():
    res = {}
    
    for f in [cycle,comprehensions,mapfilter,generator]:
        with timer:
            f()
        res[f.__name__] = timer.duration_in_seconds()
        
    return res

def test_many(n):
    results = defaultdict(lambda:0)
    for i in range(n):
        r = test()
        for k,v in r.items():
            results[k] += v 
    
    for k,v in results.items():
        results[k] /= n
    
    print 'Average of %s runs:\t %s' % (n, ',\t'.join(['%s : %s' % (r[0],r[1]) for r in results.items()]))
    
if __name__ == '__main__':
    test_many(1)
    test_many(100)
    test_many(500)
    
