#!/usr/bin/env python

import re, sys

input = '%clipboard'
r = re.compile("!\[\]\(images\/([^.]+).png\)")
m = r.match(input)
if m:
    outp = "<$img:%s>" % m.groups()[0]
else:
    outp = input
sys.stdout.write(outp)