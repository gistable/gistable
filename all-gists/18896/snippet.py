#!/usr/bin/env python3.0

import sys, array, tempfile, heapq
assert array.array('i').itemsize == 4

def intsfromfile(f):
    while True:
        a = array.array('i')
        a.fromstring(f.read(4000))
        if not a:
            break
        for x in a:
            yield x

iters = []
while True:
    a = array.array('i')
    a.fromstring(sys.stdin.buffer.read(40000))
    if not a:
        break
    f = tempfile.TemporaryFile()
    array.array('i', sorted(a)).tofile(f)
    f.seek(0)
    iters.append(intsfromfile(f))

a = array.array('i')
for x in heapq.merge(*iters):
    a.append(x)
    if len(a) >= 1000:
        a.tofile(sys.stdout.buffer)
    del a[:]
    if a:
        a.tofile(sys.stdout.buffer)