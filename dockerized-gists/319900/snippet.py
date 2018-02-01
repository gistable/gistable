import logging

# log everything
logging.basicConfig(level=logging.DEBUG)

# kickass logging for function entry/exit
class loggerize(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *a, **kw):
        logging.debug("entering " + self.f.__name__)
        x = self.f(*a, **kw)
        logging.debug("exiting " + self.f.__name__)
        return x

@loggerize
def foo():
    """will log when execution enters/exits function foo"""
    return 1 + 1
