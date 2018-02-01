#!/usr/bin/python
"""Print stats about stdin per-line timings."""

import signal
import sys
import time

start = time.time()
count = 0
try:
    for line in sys.stdin:
        count += 1
except KeyboardInterrupt:
    print
    pass
end = time.time()
et = end - start
lps = count / et
print "Elapsed time = %f, lines = %d,  lps = %f" % (et, count, lps)
