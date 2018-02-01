#!/usr/bin/python
# esc-pos-image-star.py - print image files given as command line arguments
#                         to simple ESC-POS image on stdout
#                         using ESC * \x21
# scruss - 2014-07-26 - WTFPL (srsly)

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

    # if image height is not a multiple of 24 pixels, fix that
    if im.size[1] % 24:
        im2 = Image.new('1', (im.size[0], im.size[1] + 24 - im.size[1] % 24), 'white')
        im2.paste(im, (0, 0))
        im = im2

    # Invert image, via greyscale for compatibility
    #  (no, I don't know why I need to do this)
    im = PIL.ImageOps.invert(im.convert('L'))
    # ... and now convert back to single bit
    im = im.convert('1')

    # rotate 90 degrees for output
    p_im=im.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)

    for row in range(p_im.size[0]/24):
        strip=p_im.crop((row * 24, 0, (row + 1) * 24, p_im.size[1]))
        sys.stdout.write(''.join(('\x1b*\x21',
                                  struct.pack('2B',p_im.size[1] % 256,
                                              p_im.size[1] / 256),
                                              strip.tobytes())))
                      
