#!/usr/bin/env python

import sys

filename = sys.argv[1]

# These do not remove \n
with open(filename) as f:
    s = ''.join(f.readlines())
    
with open(filename) as f:
    s = ''.join(f)
    
with open(filename) as f:
    s = f.read() # Fastest according to my tests.

# These remove \n
with open(filename) as f:
    s = ' '.join(line.replace('\n', '') for line in f)

with open(filename) as f:
    s = ' '.join(line.rstrip() for line in f)
    
with open(filename) as f:
    s = f.read().replace('\n', '')
