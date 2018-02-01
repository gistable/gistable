#!/usr/bin/env python

# Decorator Function

def log(f):
    def _inner(*a, **kw):
        print 'Calling your function'
        return f(*a, **kw)
    return _inner

@log
def foo(s):
    print s

foo('weeeeeeeeee')

# Decorator Functions + Arguments

def log_wrap(message): # receives arguments
    def _second(f): # wraps the function
        def _inner(*args, **kwargs):
            print message
            return f(*args, **kwargs)
        return _inner
    return _second


@log_wrap('Hey - imma call foo like right now')
def foo(s):
    print s

foo('weeeeeeeeee')

# Decorator Class

class Foo(object):
    def __init__(self, f):
        self.f = f # attach f to self
    def __call__(self, *a, **kw):
        print 'Calling your function'
        return self.f(*a, **kw)

@Foo
def foo(s):
    print s

foo('weeeeeeeeee')

# Decorator Class + Arguments

class Foo(object):
    def __init__(self, message):
        self.message = message
    def __call__(self, f):
        def _inner(*args):
            print self.message
            return f(*args)
        return _inner


@Foo('Hey - imma call foo like right now')
def foo(s):
    print s

foo('weeeeeeeeee')
