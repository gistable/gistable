#!/usr/bin/env python2

# -*- coding: utf-8 -*-

import sys

# RSA Decipher for SECCON CTF 4(Yokohama)
# Author: Matsukuma Hiroki a.k.a. hhc0null  <hhc.0.null@gmail.com>
# Usage: ./RSA_Decipher < [Crypted Text]

# gcd() uses the Euclidean algorithm.
def gcd(x, y):
    while y:
  x, y = y, (x % y)
    return x

# lcm() uses the theory of "LCM equals xy over GCD".
def lcm(x, y):
    return (x * y) / gcd(x,y)

# gcd_extend uses the Extend Euclidean algorithm.
def gcd_extend(x, y):
    if y == 0:
	u = 1
	v = 0
    else:
	s = x / y
	r = x % y
	(u0, v0) = gcd_extend(y, r)
	u = v0
	v = u0 - s * v0
    return (u, v)

e = 68081
n = 17777777
p = 283
q = 62819

l = lcm(p-1, q-1)
d = gcd_extend(e,l)[0]
if d < 0:
    d += l

list = []
for line in sys.stdin:
    m = pow(int(line), d, n)
    list.append(chr(m))

print "".join(list)
