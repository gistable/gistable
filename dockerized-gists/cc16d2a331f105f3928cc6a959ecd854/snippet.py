#!/usr/bin/env python3
import operator, re, sys
from functools import reduce
def f(a,x):
  # NB: currently ignores fractions of seconds
  mo    = re.search(r"(([0-9]{2}:){1,2}([0-9]{2}))(\.[0-9]{2})?", x)
  hms   = tuple(map(int, mo.group(1).split(":")))
  hms_  = hms if len(hms) == 3 else tuple([0] + list(hms))
  h,m,s = map(operator.add, a, hms_); m_ = m+s//60
  return (h+m_//60,m_%60,s%60)
h,m,s = reduce(f, sys.stdin, (0,0,0))
print("{:02d}:{:02d}:{:02d}".format(h,m,s))
