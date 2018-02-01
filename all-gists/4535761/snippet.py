import time
def timer():
    start = time.time()
    return lambda: time.time() - start

def timed(callback=None):
    if callback is None:
        callback = lambda *a, **kw: None
    def wrapper(func):
        def wrapped_call(*args, **kwargs):
            _time = timer()
            ret = func(*args, **kwargs)
            delta = _time()
            callback(delta)
            return ret
        return wrapped_call
    return wrapper

### USAGE

def some_slow_function(n):
    time.sleep(n)

def printer(delta):
    print "Done in %s seconds." % delta

_time = timer()
some_slow_function(0.5)
delta = _time()
printer(delta)

### DECORATOR USAGE
def printer(delta):
    print "Decorated Done in %s seconds." % delta

@timed(printer)
def another_slow_function(n):
    time.sleep(n)

another_slow_function(1)