#-*- coding:utf-8 -*-

import random
from z3 import *

s = Solver()

htest = random.randint(0, 1<<32-1)
print hex(htest)

def shr32(v, n):
    return (v >> n) & ((1 << (32-n)) - 1)

xs = list(BitVecs('c0 c1 c2 c3 c4 c5', 32))

h = BitVec('hs', 32)
s.add(h == 0x4E67C6A7)

for i, c in enumerate(xs):
    s.add(c >= 0)
    s.add(c < 255)

    h = h ^ (shr32(h, 2) + (h << 5) + c)

s.add(h == htest)

print s.check()
m = s.model()
print m


def hash(s):
    h = 0x4E67C6A7
    for i, c in enumerate(s):
        a = (h >> 2) & 0xffffffff
        b = (h << 5) & 0xffffffff
        h = h ^ ( a + b + ord(c) )
        h &= 0xffffffff
    return h

s = "".join([chr( m[c].as_long() ) for c in xs])
print hex(hash(s))
