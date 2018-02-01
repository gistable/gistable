#!/usr/bin/env python

from glob import glob
import re

def backend(path):
    return path.split('/')[3].replace('-', '_').replace('.', '_')

def site(path):
    return path.split('/')[7]

def hostnames(path):
    s = open(path + "/config").read()
    h = re.findall('hostname, "(.*?)"', s, re.M)
    a = re.findall('hostalias, "(.*?)"', s, re.M)
    a2 = re.findall('hostalias, (\[.*?\])', s, re.M)
    a2 = sum([eval(x) for x in a2], [])
    return h + a + a2

all = {}
    
for d in glob("/home/zotonic/zotonic-*/zotonic/priv/sites/*"):
    s = site(d)
    b = backend(d)
    if s in ('testsandbox', 'zotonic_status'):
        continue
    if b not in all:
        all[b] = []
    all[b] += hostnames(d)

#print all

print "#"
print "# Auto-generated Varnish Zotonic backend switch"
print "#"
first = True
for b in all:
    if first:
        print "if (",
    else:
        print "elseif (",

    print " || ".join(["req.http.host ~ \"^%s$\"" % h for h in all[b]]),
    
    print ") {"
    print "  set req.backend = " + b + ";"
    print "}"
    first = False
    
print
