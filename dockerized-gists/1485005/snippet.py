#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

WIDE_MAP = dict((i, i + 0xFEE0) for i in xrange(0x21, 0x7F))
WIDE_MAP[0x20] = 0x3000

def widen(s):
    """
    Convert all ASCII characters to the full-width counterpart.
    
    >>> print widen('test, Foo!')
    ｔｅｓｔ，　Ｆｏｏ！
    >>> 
    """
    return unicode(s).translate(WIDE_MAP)

while True:
    line = sys.stdin.readline()
    if not line: break
    sys.stdout.write(widen(line.decode('utf-8')).encode('utf-8'))
