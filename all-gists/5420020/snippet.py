#!/usr/bin/python

import sys
from PIL import Image

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 64.
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)

def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s img1 img2" % sys.argv[0]
    else:
        img1 = sys.argv[1]
        img2 = sys.argv[2]
        hash1 = avhash(img1)
        hash2 = avhash(img2)
        dist = hamming(hash1, hash2)
        print "hash(%s) = %d\nhash(%s) = %d\nhamming distance = %d\nsimilarity = %d%%" % (img1, hash1, img2, hash2, dist, (64 - dist) * 100 / 64)
