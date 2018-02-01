import sys
import time
import resource

s = sys.argv[1].split('.')
lru = __import__(s[0]).__dict__[s[1]]

m = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
t = time.clock()

cache = lru(1000000)
for i in xrange(1100000):
  cache[i] = i

print "Time : %r s, Memory : %r Kb" % (time.clock()-t,
      resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - m)
