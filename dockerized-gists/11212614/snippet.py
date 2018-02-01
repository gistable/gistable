#!/usr/bin/env python2

# There should be a standard way of doing this. For now a hack.

import gevent
import inspect


def one():
    print '1'
    gevent.sleep(1)
    print '2'


def two():
    print '3'
    print '4'


class FrameWriter:

    def off(self):
        sys.stdout = self.stdout

    def on(self):
        self.stdout = sys.stdout
        sys.stdout = self

    def __init__(self):
        self.stdout = None
        self.writers = {}

    def write(self, obj):
        caller = inspect.stack()[2][0].f_locals['self']  # Greenlets specific.
        if not caller in self.writers:
            self.writers[caller] = StringIO.StringIO()
        self.writers[caller].write(obj)

    def get_value(self, caller):
        value = self.writers[caller].getvalue()
        del self.writers[caller]
        return value

import sys
import StringIO

frame_writer = FrameWriter()
frame_writer.on()

a = gevent.spawn(one)
b = gevent.spawn(two)
c = gevent.spawn(one)

# print one
gevent.joinall([a, b, c])
frame_writer.off()
print frame_writer.get_value(c)
