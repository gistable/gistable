#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Video of this screencast: https://vimeo.com/57296525
# 
# 
from __future__ import print_function, division, absolute_import
from PIL import Image as pImage
import numpy

import os
import random

class Image:
    """Take an information from image file"""

    BLOCK_SIZE = 20
    TRESHOLD = 60

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        img = pImage.open(self.filename)
        small = img.resize( (Image.BLOCK_SIZE, Image.BLOCK_SIZE),
                            pImage.BILINEAR )
        self.t_data = numpy.array(
            [sum(list(x)) for x in small.getdata()]
        )
        del img, small
        return self

    def __repr__(self):
        return self.filename

    def __mul__(self, other):
        return sum(1 for x in self.t_data - other.t_data if abs(x) > Image.TRESHOLD)

class ImageList:
    """List of images information, built from directory.
    All files must be *.jpg"""
    def __init__(self, dirname):
        self.dirname = dirname
        self.load()

    def load(self):
        self.images = \
            [Image(os.path.join(self.dirname, filename)).load() \
                for filename in os.listdir(self.dirname)
                    if filename.endswith('.jpg')]
        random.shuffle(self.images)
        return self

    def __repr__(self):
        return '\n'.join( ( x.filename for x in self.images ) )

    def html(self):
        res = ['<html><body>']
        for img in self.images:
            distances = sorted([ (img * x, x) for x in self.images ])
            res += [
                '<img src="' + os.path.basename(x.filename) + '" width="200"/>' + str(dist)
                for dist, x in distances if dist < 220]
            res += ['<hr/>']
        res += ['</body></html>']

        return '\n'.join(res)

if __name__ == '__main__':
    il = ImageList('/Users/bobuk/,misc/wm')
    print(il.html())
