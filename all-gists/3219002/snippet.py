#!/usr/bin/env python

from ctypes import CDLL

foo = "Fiesta"
bar = "Fiesta"

#Change foo with low level C
libc = CDLL('libc.so.6')
libc.strcpy(foo, "Nachos")


print "We'll meet at the", bar
