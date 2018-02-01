# -*- encoding: utf-8 -*-

import sys
#print sys.argv

if len(sys.argv) < 3:
  print "usage: %s [start] [end]" % sys.argv[0]
  sys.exit(1)

start = int(sys.argv[1])
end = int(sys.argv[2])

import redis
redis = redis.Redis(host='localhost', port=6379, db=0)

if len(sys.argv) >= 4 and sys.argv[3] == "flushall":
  redis.flushall()

import time

s_time = time.time()

with redis.pipeline() as pipe:
  pipe.multi()

  for i in xrange(start, end):
    id = "%040x" % i
    key = "abc:defghi"
    ret = pipe.sadd(key, id)

    if (i+1) % 1000 == 0:
      print "Now cnt: %d" % (i+1)
      pipe.execute()
      pipe.multi()

  print "Execute..."
  pipe.execute()

e_time = time.time()

print "Done..."
print "Elapsed time: %0.2f" % (e_time - s_time)
