#!/usr/bin/env python

"""Functions to convert IPv4 address to integer and vice-versa.

Written by Christian Stigen Larsen, http://csl.sublevel3.org
Placed in the public domain by the author, 2012-01-11

Example usage:
$ ./ipv4 192.168.0.1 3232235521
192.168.0.1 ==> 3232235521
3232235521 ==> 192.168.0.1
"""

import sys

def from_string(s):
  "Convert dotted IPv4 address to integer."
  return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def to_string(ip):
  "Convert 32-bit integer to dotted IPv4 address."
  return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print "Usage: ipv4 [ (address | integer)* ]"
    print "Converts between IPv4 addresses and integers."
    print ""
    print "Example usage:"
    print "$ ./ipv4 192.168.0.1 3232235521"
    print "192.168.0.1 ==> 3232235521"
    print "3232235521 ==> 192.168.0.1"
    print ""
    print "Written by Christian Stigen Larsen, http://csl.sublevel3.org"
    print "Placed in the public domain by the author, 2012-01-11"
    sys.exit(0)

  for arg in sys.argv[1:]:
    if arg.count(".") == 3:
      print arg, "==>", from_string(arg)
    else:
      try:
        print arg, "==>", to_string(int(arg))
      except Exception, e:
        print "Not an integer or dotted IPv4 address:", arg
        sys.exit(1)
