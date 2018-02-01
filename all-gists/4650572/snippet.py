#!/usr/bin/python
#
# Example usage
# $ ./gangnam.py | gnuplot
# 9
# 0 0
# 1 1
# 2 2
# 0 2
# 1 1
# -1 1
# 0 2
# -2 2
# -1 1

import math

N = int(raw_input())

f = []
for i in xrange(0, N):
  (x, y) = [int(x) for x in raw_input().split()]
  f.append(complex(x, y))

F = []
for i in xrange(0, N):
  ang = -2 * math.pi * i / N
  rt = complex(math.cos(ang), math.sin(ang))
  w = 1
  r = 0
  for j in xrange(0, N):
    r += f[j] * w
    w *= rt
  F.append(r)

print "set parametric"
print "set samples", N + 1

print "plot [t=0:", N, "]",
for i in xrange(0, N):
  ang = 2 * math.pi * i / N
  arg = math.atan2(F[i].imag, F[i].real)
  if i > 0:
    print "+",
  print abs(F[i]) / N, "* cos(", arg, "+", ang, "* t)",

print ",",

for i in xrange(0, N):
  ang = 2 * math.pi * i / N
  arg = math.atan2(F[i].imag, F[i].real)
  if i > 0:
    print "+",
  print abs(F[i]) / N, "* sin(", arg, "+", ang, "* t)",

print
print "pause 555"