#!/usr/bin/python 
# Connects to localhost, 27017 by default

import sys
import pymongo
import time

if len(sys.argv) < 2:
    print >> sys.stderr, "Usage: ./tail_profile.py <dbName> [hostname] [port]"
    sys.exit(-1)

host = 'localhost'
port = 27017


if len(sys.argv) >= 3:
  host = sys.argv[2]

if len(sys.argv) >= 4:
  port = int(sys.argv[3])

print "Connecting to Mongo at %s:%i" % (host, port)
time.sleep(3)

try:
    db = pymongo.Connection(host, port, slave_okay=True)[sys.argv[1]]
except:
    print >> sys.stderr, "Connection failed to %s:%i.  Please check the host and try again."
    sys.exit(-1)

if 'system.profile' not in db.collection_names():
    print >> sys.stderr, "Query profiling not enabled. Please see http://www.mongodb.org/display/DOCS/Database+Profiler"
    sys.exit(-1)

mongo = db['system.profile']

cursor = mongo.find(tailable=True).sort("$natural", 1)

while cursor.alive:
    try:
      print cursor.next()
    except StopIteration:
      time.sleep(1)