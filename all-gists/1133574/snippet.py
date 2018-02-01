import functools

class generatorfunction(object):
    """
    Apparently you can't monkeypatch generator objects for some reason.
    Lets go ahead and proxy them instead to add __call__.
    """

    def __init__(self, generator):
        self.delegate = generator

    def __getattr__(self, key):
        if key == '__call__':
            return self.__call__
        else:
            return getattr(self.delegate, key)
        
    def __call__(self, *args):
        if args:
            print "calling send", args
            return self.send(*args)
        else:
            print "calling next"
            return self.next()

def coroutine(fn):
    functools.wraps(fn)
    def wrapped(*args, **kwargs):
        g = generatorfunction(fn(*args, **kwargs))
        g()  # get to the first yield
        g(g)  # and pass it `self`
        return g
    return wrapped

@coroutine
def calcfib(cofn):
    self = (yield)
    cur = (yield)
    while True:
        print "calcfib loop", cur,
        cur = cofn(cur + 1)

@coroutine
def cofib():
    self = (yield)
    cofn = calcfib(self)
    cur = (yield)
    while True:
        print "cofib loop", cur, 
        cur = cofn(cur + 1)

fn = cofib()
fn(5)

