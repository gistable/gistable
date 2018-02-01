import sys
import redis

if len(sys.argv) == 0:
    print "Usage: redis-db-mem.py HOST [PORT]"
    sys.exit(2)

host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])
else:
    port = 6379

info = redis.StrictRedis(host, port).info()
dbs = [int(_[2:]) for _ in info if _[0:2] == 'db']
dbs.sort()
total_bytes = 0
for db in dbs:
    r = redis.StrictRedis(host, port, db=db)
    key_count = 0
    byte_count = 0
    for key in r.scan_iter('*'):
        object_dump = r.dump(key)
        if object_dump:
            key_count += 1
            byte_count += len(object_dump) - 8
    total_bytes += byte_count
    print "db %d: %d objects, %d bytes" % (db, key_count, byte_count)

print "total: %d bytes"
