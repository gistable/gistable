#!/usr/bin/env python
#
# based on http://stackoverflow.com/a/2753343o
#
# input needs to be presorted
#

import math
import functools
import fileinput

def percentile(N, percent, key=lambda x:x):
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
	return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

numbers = []

for line in fileinput.input():
    numbers.append(float(line))

print percentile(numbers, 0.95)