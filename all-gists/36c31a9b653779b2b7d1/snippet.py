#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

# if you want a proper CUPS driver for a 58mm thermal printer
# that uses this command set, go here:
#            https://github.com/klirichek/zj-58

import sys
from PIL import Image
import PIL.ImageOps
import struct

# give usage and exit if no arguments
if len(sys.argv) == 1:
    print 'Usage:', sys.argv[0], \
           'image1 image2 ... [ > printer_device ]'
    exit(1)

# print all of the images!
for i in sys.argv[1:]:
    im = Image.open(i)

    # if image is not 1-bit, convert it
    if im.mode != '1':
        im = im.convert('1')

    # if image width is not a multiple of 8 pixels, fix that
    if im.size[0] % 8:
        im2 = Image.new('1', (im.size[0] + 8 - im.size[0] % 8,
                        im.size[1]), 'white')
        im2.paste(im, (0, 0))
        im = im2

    # Invert image, via greyscale for compatibility
    #  (no, I don't know why I need to do this)
    im = PIL.ImageOps.invert(im.convert('L'))
    # ... and now convert back to single bit
    im = im.convert('1')

    # output header (GS v 0 \000), width, height, image data
    sys.stdout.write(''.join(('\x1d\x76\x30\x00',
                              struct.pack('2B', im.size[0] / 8 % 256,
                                          im.size[0] / 8 / 256),
                                          struct.pack('2B', im.size[1] % 256,
                                                      im.size[1] / 256),
                                                      im.tobytes())))
