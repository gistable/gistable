#!/usr/bin/env python3

import sys


ORDER = [0, 7, 2, 5, 4, 3, 6, 1]
SRC = sys.argv[1]
DEST = sys.argv[2]


with open(SRC, "rb") as f:
    org = f.read()

with open(DEST, "wb") as dec:
    size = (len(org) - 128) >> 3
    dec.write(org[0:128])
    for i in ORDER:
        dec.write(org[ i*size+128 : (i+1)*size+128 ])