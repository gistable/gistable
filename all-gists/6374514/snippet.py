import gevent

from gevent import httplib

def fetcher():
    print "fetcher: Fetching..."
    conn = httplib.HTTPConnection("www.google.com")
    conn.request("GET", "/")
    res = conn.getresponse()
    output = res.read()
    print "fether: Received %s bytes" % len(output)

print "main: Spawning..."
g = gevent.spawn(fetcher)
print "main: Spawned."
gevent.sleep(0)
print "main: Sleeped."
gevent.joinall([g])
print "main: Joined."