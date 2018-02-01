from __future__ import with_statement
import signal, time
from contextlib import contextmanager

def long_function_call():
    while True:
        if time.time() % 1 == 0:
            print '*'

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


try:
    with time_limit(3):
        long_function_call()
except TimeoutException, msg:
    print msg