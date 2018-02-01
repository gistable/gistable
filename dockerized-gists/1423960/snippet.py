#!/usr/bin/env python
import re
import sys
from urllib import urlopen

def isup(domain):
    resp = urlopen("http://www.isup.me/%s" % domain).read()
    return "%s: %s" % (domain, "UP" if re.search("It's just you.", resp, 
        re.DOTALL) else "DOWN")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print "\n".join(isup(d) for d in sys.argv[1:])
    else:
        print "usage: %s domain1 [domain2 .. domainN]" % sys.argv[0]
