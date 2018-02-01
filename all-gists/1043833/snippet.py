#!/usr/bin/env python

import logging
import time

logging.basicConfig(level=logging.DEBUG,
                    filename='whatevz.log')

def log_runtime(method):
    def wrapper(*a, **kw):
        start = time.time()
        retval = method(*a, **kw)
        finish = time.time()
        logging.debug('%s took %s seconds to run' % (method.__name__,
                                                     (finish - start)))
        return retval
    return wrapper


@log_runtime
def foo():
    print 'foo'

if __name__ == "__main__":
    foo()