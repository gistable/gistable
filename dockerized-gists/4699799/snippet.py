#!/usr/bin/env python
import sys
keep = {}


for line in sys.stdin.readlines():
    mountpoint = line.rfind("-")
    if not line[:3] + line[mountpoint:] in keep:
        keep[line[:3] + line[mountpoint:]] = line
    else:
        sys.stdout.write(line)