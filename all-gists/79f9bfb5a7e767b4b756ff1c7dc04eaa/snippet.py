#!/usr/bin/env python
# coding: utf-8

import os
import sys

from PIL import Image, ImageChops

templates = []

def generate_templates(path):
    img = Image.open(path)
    r, g, b, a = img.split()
    bw = g.point(lambda x: 0 if x<10 else 255, '1')
    for i in range(4):
        bw.crop((5+i*7, 5, 5+i*7+6, 5+10)).save('{}_{}.png'.format(path, i))


def read_templates():
    for i in range(10):
        templates.append(Image.open('{}.png'.format(i)))


def recognise(path):
    img = Image.open(path)
    r, g, b, a = img.split()
    bw = g.point(lambda x: 0 if x<10 else 255, '1')
    result = ''
    for i in range(4):
        num = bw.crop((5+i*7, 5, 5+i*7+6, 15))
        diff = [sum(ImageChops.difference(num, templates[j]).getdata()) / 255 for j in range(10)]
        result += str(diff.index(min(diff)))
    return result


read_templates()
for subdir, dirs, files in os.walk('.'):
    for f in files:
        if not f.endswith('.jpg'):
            continue
        f = os.path.join(subdir, f)
        num = os.path.basename(f)
        result = recognise(f)
        print 'file: {}, result: {}'.format(num, result)
