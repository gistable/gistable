#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------

import redis, random

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

NUSERS = 10000
NTAGS = 500
NBUCKETS = 1000

# ----------------------------------------------------
# Fill redis with some random data

def fill(r):
  p = r.pipeline()
  # Create only 10000 users for this example
  for id in range(0,NUSERS):
    user = "user:%d" % id
    # Add the user in the index: a simple modulo is used to hash the user id
    # and put it in the correct bucket
    p.sadd( "index:%d" % (id%NBUCKETS), user )
    # Add random tags to the user
    for x in range(0,20):
      tag = "tag:%d" % (random.randint(0,NTAGS))
      p.zincrby( user, tag, 1 )
    # Flush the pipeline every 1000 users
    if id % 1000 == 0:
      p.execute()
      print id
  # Flush one last time
  p.execute()

# ----------------------------------------------------
# Iterate on all the users and displays their 5 highest ranked tags

def iterate(r):
  # Iterate on the buckets of the key index
  # The range depends on the function used to hash the user id
  for x in range(0,NBUCKETS):
    # Iterate on the users in this bucket
    for user in r.smembers( "index:%d"%(x) ):
      print user,r.zrevrangebyscore(user,"+inf","-inf", 0, 5, True )

# ----------------------------------------------------
# Main function

def main():
  r = redis.Redis(connection_pool=POOL)
  r.flushall()
  m = r.info()["used_memory"]
  fill(r)
  info = r.info()
  print "Keys: ",info["db0"]["keys"]
  print "Memory: ",info["used_memory"]-m
  iterate(r)

# ----------------------------------------------------

    main()
