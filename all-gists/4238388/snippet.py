from functools import wraps
from timeit import default_timer
import gevent
from gevent.queue import Queue

def gevent_throttle(calls_per_sec=0):
    """Decorates a Greenlet function for throttling."""
    interval = 1. / calls_per_sec if calls_per_sec else 0
    def decorate(func):
        blocked = [False] # has to be a list to not get localised inside the while loop
        # otherwise, UnboundLocalError: local variable 'blocked' referenced before assignment
        last_time = [0] # ditto
        @wraps(func) # propagates docstring
        def throttled_func(*args, **kwargs):
            while True:
                # give other greenlets a chance to run, otherwise we
                # might get stuck while working thread is sleeping and the block is ON
                gevent.sleep(0)
                if not blocked[0]:
                    blocked[0] = True
                    # check if actually might need to pause
                    if calls_per_sec:
                        last, current = last_time[0], default_timer()
                        elapsed = current - last
                        if elapsed < interval:
                            gevent.sleep(interval - elapsed)
                        last_time[0] = default_timer()
                    blocked[0] = False
                    return func(*args, **kwargs)
        return throttled_func
    return decorate

# possible use

import requests
from gevent.pool import Pool

pool = Pool()

@gevent_throttle(10)
def worker(address):
    """somd doc"""
    print address
    url='http://maps.googleapis.com/maps/api/geocode/json'
    params = dict(address=address, sensor='false')
    json = requests.get(url, params=params).json
    return json

jobs = pool.imap(worker, 'NYC LA SF Chicago Boston Austin Portland'.split())