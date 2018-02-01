#!/usr/bin/env python

# you may need to apt-get install python-imaging

import sys
from PIL import Image

def red(filename):
    image = Image.open(filename)
    for r, g, b in image.getdata():
        if r < g and r < b:
            return False
    return True

filename = sys.argv[1]
print red(filename)