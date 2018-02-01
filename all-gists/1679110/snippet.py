#!/usr/bin/python

# You need to install PIL & argparse
# easy_install is your friend, pip is your better friend.

import os
from PIL import Image
import argparse

parser = argparse.ArgumentParser(description='Find (or purple-ize!) images without @2x counterparts')
parser.add_argument('directory', metavar='DIRECTORY', type=str, nargs=1,
                   help='Path to image directory')
parser.add_argument('--color', dest='color', action='store_true',
                   default=False,
                   help='Overwrite the original image with purple pixels')

args = parser.parse_args()
print args.directory

theRoot = args.directory[0]

theOneXImages = set()
theTwoXImages = set()

for root, dirs, files in os.walk(theRoot):
    if '.DS_Store' in files:
        del files[files.index('.DS_Store')]

    for f in files:
        f = os.path.join(root, f)
        if '@2x' in f:
            theTwoXImages.add(f)
        else:
            theOneXImages.add(f)

theLonesomeImages = set()
theRetinaImages = set()
for f in theOneXImages:
    theName, theExtension = os.path.splitext(f)
    the2XName = theName + '@2x' + theExtension
    if the2XName not in theTwoXImages:
        theLonesomeImages.add(f)
    else:
        theRetinaImages.add(f)

for f in theLonesomeImages:
    print f
    if args.color:
        im = Image.open(f)
        theSize = im.size
        im = Image.new('RGBA', theSize, (255, 0, 255, 255))
        im.save(f)
