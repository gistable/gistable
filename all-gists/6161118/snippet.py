#!/usr/bin/env python

# jsonenv reads a json object as input and produces
# escaped shell commands for setting environment vars

import json
import pipes
import sys

for k, v in json.load(sys.stdin).items():
    k = pipes.quote(k)
    v = pipes.quote(v)
    print "%s=%s export %s;" % (k, v, k)
