#!/usr/bin/env python

import unicodedata, sys

def uninamenum(c):
    u = 'U+%04X' % ord(c)
    try:
        name = unicodedata.name(c)
    except:
        return u
    else:
        return u + ' ' + name.title()

import ctypes
wcwidth = ctypes.CDLL(None).wcwidth
wcwidth.argtypes = [ctypes.c_wchar]
def printable_char(c):
    return (c if wcwidth(c) >= 0 else '')
def describe(chunk):
    return '\n'.join('%s\t%s' % (printable_char(c), uninamenum(c))
                     for c in chunk.rstrip('\n'))
print('\n\n'.join(filter(None, map(describe, (sys.stdin if len(sys.argv) == 1
                                              else sys.argv[1:])))))