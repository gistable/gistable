#!/usr/bin/env python
import re, sys
for l in sys.stderr.readlines():
    url = re.findall(r'http:.+\.deb', l)
    if len(url):
        print url[0]