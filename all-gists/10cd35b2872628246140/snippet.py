#!/usr/bin/python3
# vim:fileencoding=utf-8:sw=4:et

# Convert between pygobject Pixbuf and PIL/Pillow image format
# Also a function to do fast gamma correction with Pillow image

from __future__ import print_function, unicode_literals, absolute_import
import sys

from gi.repository import GLib, GdkPixbuf
from PIL import Image

def pixbuf2image(pix):
    """Convert gdkpixbuf to PIL image"""
    data = pix.get_pixels()
    w = pix.props.width
    h = pix.props.height
    stride = pix.props.rowstride
    mode = "RGB"
    if pix.props.has_alpha == True:
        mode = "RGBA"
    im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
    return im

def image2pixbuf(im):
    """Convert Pillow image to GdkPixbuf"""
    data = im.tobytes()
    w, h = im.size
    data = GLib.Bytes.new(data)
    pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
            False, 8, w, h, w * 3)
    return pix

def do_gamma(im, gamma):
    """Fast gamma correction with PIL's image.point() method"""
    invert_gamma = 1.0/gamma
    lut = [pow(x/255., invert_gamma) * 255 for x in range(256)]
    lut = lut*3 # need one set of data for each band for RGB
    im = im.point(lut)
    return im

def test_i2p(infile, outfile):
    im = Image.open(infile)
    pix = image2pixbuf(im)
    pix.savev(outfile, "png", (), ())

def test_p2i(infile, outfile):
    pix = GdkPixbuf.Pixbuf.new_from_file(infile)
    im = pixbuf2image(pix)
    # FIXME: We also test gamma correction here
    im = do_gamma(im, 1.8)
    im.save(outfile)

def main():
    infile = sys.argv[1]
    outfile = "pixpil-test.png"
    test_p2i(infile, outfile)
    #test_i2p(infile, outfile)
    print("result saved to {}".format(outfile))

if __name__ == '__main__':
    main()

