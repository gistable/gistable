#!/usr/bin/env python

import sys
import re

def convert(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()
        return re.sub('[./_]+', '_', s2)

prefix = sys.argv[1]
filename = sys.argv[2]
f = open(filename)

line = f.readline()
if not line.startswith("#ifndef"):
        raise Exception("file does not start with include guard")

line = f.readline()
if not line.startswith("#define"):
        raise Exception("file does not start with include guard")

content = []
for line in f:
    content.append(line)
f.close()

includeGuard = convert("%s%s" % (prefix, filename))
o = open(filename, 'w')
o.write("#ifndef " + includeGuard + "\n")
o.write("#define " + includeGuard + "\n")

for line in content:
        o.write(line)
