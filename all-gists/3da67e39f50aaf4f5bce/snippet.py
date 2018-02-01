"""Extract mean, median and percentiles from `nodetool cfhistogram` output.

Usage:

  1. Run this script.
  2. Paste in the output from a read or write latency histograms.
  3. Press CTRL+D (to close stdin file descriptor).
"""
import sys
import collections

def percentile(records, p, total_counts):
  assert 0 <= p <= 1
  cumsum = 0
  percentile_count = int(round(p * total_counts))
  for r in records:
    cumsum += r.count
    if cumsum >= percentile_count:
      return r.duration

Record = collections.namedtuple('Record', ('duration', 'count'))
records = [Record(*[int(k) for k in line.strip().split(' us: ')]) for line in sys.stdin if 'us:' in line]
total_counts = sum([r.count for r in records])

print "Average:         {0:.2f} us".format(1.0 * sum([r.duration*r.count for r in records]) / total_counts)
print "Min:             {0:.2f} us".format(percentile(records, 0, total_counts))
print "1% percentile:   {0:.2f} us".format(percentile(records, 0.01, total_counts))
print "10% percentile:  {0:.2f} us".format(percentile(records, 0.1, total_counts))
print "Median:          {0:.2f} us".format(percentile(records, 0.5, total_counts))
print "90% percentile:  {0:.2f} us".format(percentile(records, 0.9, total_counts))
print "99% percentile:  {0:.2f} us".format(percentile(records, 0.99, total_counts))
print "Max:             {0:.2f} us".format(percentile(records, 1, total_counts))