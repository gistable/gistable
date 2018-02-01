'''From http://www.daniweb.com/software-development/python/code/216610
Modified to use logging instead of print statments

Usage:
@log_time
def my_function():
    pass
'''

import logging
import time

def log_time(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        t2 = time.time()
        logging.info('%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0))
        return res
    return wrapper