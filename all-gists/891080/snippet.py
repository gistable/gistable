#! /usr/bin/env python

from geoserver.catalog import Catalog

cat = Catalog('http://host/geoserver/rest', 'user', 'password')

def internal_name(s):
    return s.startswith("__") and s.endswith("__")

def check(x):
    if hasattr(x, 'name'):
        print "NAME:", x.name, " TYPE:", type(x)
    for name in dir(x):
        if not internal_name(name) and getattr(x, name) is None:
            print x, name, "IS NONE"

for ws in cat.get_workspaces(): 
    check(ws)

for st in cat.get_stores():
    check(st)

    for rs in cat.get_resources(st):
        check(rs)