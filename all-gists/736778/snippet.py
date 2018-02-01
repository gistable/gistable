#!/usr/bin/env python

# simple benchmark comparing with and try statements

import contextlib
import timeit

def work_pass():
    pass

def work_fail():
    1/0

def simple_catch(fn):
    try:
        fn
    except Exception:
        pass

@contextlib.contextmanager
def catch_context():
    try:
        yield
    except Exception:
        pass

def with_catch(fn):
    with catch_context():
        fn()

class ManualCatchContext(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

def manual_with_catch(fn):
    with ManualCatchContext():
        fn()

setup = 'from __main__ import simple_catch, work_pass, work_fail, with_catch, manual_with_catch'
commands = [
    'simple_catch(work_pass)',
    'simple_catch(work_fail)',
    'with_catch(work_pass)',
    'with_catch(work_fail)',
    'manual_with_catch(work_pass)',
    'manual_with_catch(work_fail)',
    ]
for c in commands:
    print c, ': ', timeit.timeit(c, setup)

# simple_catch(work_pass) :  0.190114021301
# simple_catch(work_fail) :  0.190967082977
# with_catch(work_pass) :  5.82143998146
# with_catch(work_fail) :  9.16547012329
# manual_with_catch(work_pass) :  1.06963706017
# manual_with_catch(work_fail) :  1.43239498138
