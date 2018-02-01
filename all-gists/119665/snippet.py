# -*- coding: utf-8 -*-
# pipes.py - Command-piping syntax for generators/coroutines in Python.

"""
pipes.py - Command-piping syntax for generators/coroutines in Python.

Example:
    
    >>> from pipes import *
    >>> chain1 = counter(5) | adder(2)
    >>> for i in chain1:
    ...     print i
    2
    3
    4
    5
    6
    >>> chain2 = counter(5) | adder(3) | printer()
    >>> results = list(chain2)
    3
    4
    5
    6
    7
    >>> print results
    [None, None, None, None, None]
    >>> chain3 = counter(5) | adder(3) | tee(printer())
    >>> results = list(chain3)
    3
    4
    5
    6
    7
    >>> print results
    [3, 4, 5, 6, 7]
"""

from functools import wraps


def attrproxy(*attrs):
    """Make top-level references to deeper attributes."""
    def fget(self):
        return getattr(reduce(getattr, attrs[:-1], self), attrs[-1])
    def fset(self, value):
        return setattr(reduce(getattr, attrs[:-1], self), attrs[-1], value)
    def fdel(self):
        return delattr(reduce(getattr, attrs[:-1], self), attrs[-1])
    return property(fget, fset, fdel)


class pipe(object):
    
    def __init__(self, coroutine):
        self.coroutine = coroutine
    
    def __or__(self, other_coroutine):
        def pump():
            for item in self.coroutine:
                yield (other_coroutine.send(item))
        return pipe(pump())
    
    for attr in ['next', 'send', 'throw', 'close', '__iter__']:
        vars()[attr] = attrproxy('coroutine', attr)


def producer(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return pipe(function(*args, **kwargs))
    return wrapper


def consumer(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        coro = function(*args, **kwargs)
        # The following line is the difference between the `producer()` and
        # `consumer()` decorators. Consumers need to be 'started' before they
        # can start receiving values, whereas producers yield values from the
        # beginning.
        coro.next()
        return pipe(coro)
    return wrapper


## Some example definitions of producers and consumers.

@producer
def counter(*args):
    """Accepts all the arguments of ``xrange()`` but works well with pipes."""
    for i in xrange(*args):
        yield i

@consumer
def adder(num):
    """Adds a constant to everything it receives."""
    val = (yield)
    while True:
        val = (yield val + num)

@consumer
def identity():
    """Yields what it receives."""
    val = (yield)
    while True:
        val = (yield val)

@consumer
def printer():
    """Prints what it receives."""
    while True:
        print (yield)

@consumer
def tee(target):
    """Both yields received values and sends them to a target."""
    val = (yield)
    while True:
        target.send(val)
        val = (yield val)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
