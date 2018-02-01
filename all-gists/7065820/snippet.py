#! /usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import struct, os, sys

def usage():
    print './png2rgb565.py HOGE.png'
    sys.exit(1)
    
def error(msg):
    print msg
    sys.exit(-1)
    
def write_bin(f, pixel_list):
    for pix in pixel_list:
        r = (pix[0] >> 3) & 0x1F
        g = (pix[1] >> 2) & 0x3F
        b = (pix[2] >> 3) & 0x1F
        f.write(struct.pack('H', (r << 11) + (g << 5) + b))

##
if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2: usage()
    in_path = args[1]
    if os.path.exists(in_path) == False: error('not exists: ' + in_path)
    
    body, _ = os.path.splitext(in_path)
    out_path = body + '.bin'

    img = Image.open(in_path).convert('RGB')
    pixels = list(img.getdata())
    # print pixels
    
    with open(out_path, 'wb') as f:
        write_bin(f, pixels)

