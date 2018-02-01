import math
import sys

def percentile(data, percentile):
    size = len(data)
    return data[int(math.floor(size * percentile / 100.0 + 0.5)) - 1]

p = list()
for line in sys.stdin:
    try:
        p.append(float(line))
    except ValueError:
        pass

for pval in (99, 95, 85, 50, 25, 10, 5):
    print("percentile {0:02d}: {1}".format(pval, percentile(p, pval)))
