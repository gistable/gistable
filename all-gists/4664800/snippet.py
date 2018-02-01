#!/usr/bin/env python
#
# Corey Goldberg, 2013
#
# Python 2.7


"""validate and analyze dimensions of image files.  Supports: PNG, JPG, GIF."""


import StringIO
import struct


def is_gif(data):
    return (data[:6] in ('GIF87a', 'GIF89a'))


def is_png(data):
    return ((data[:8] == '\211PNG\r\n\032\n') and (data[12:16] == 'IHDR'))


def is_old_png(data):
    return ((data[:8] == '\211PNG\r\n\032\n') and (data[12:16] != 'IHDR'))


def is_jpeg(data):
    return (data[:2] == '\377\330')


def get_image_dimensions(data):
    if len(data) < 16:
        raise Exception('not valid image data')

    elif is_gif(data):
        w, h = struct.unpack('<HH', data[6:10])
        width = int(w)
        height = int(h)

    elif is_png(data):
        w, h = struct.unpack('>LL', data[16:24])
        width = int(w)
        height = int(h)

    elif is_old_png(data):
        w, h = struct.unpack('>LL', data[8:16])
        width = int(w)
        height = int(h)
        
    elif is_jpeg(data):
        jpeg = StringIO.StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = jpeg.read(1)
                while (ord(b) == 0xFF): b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack('>HH', jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack('>H', jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    else:
        raise Exception('not valid image data')
        
    return width, height


if __name__ == '__main__':
    with open('foo.png', 'rb') as f:
        data = f.read()
    w, h = get_image_dimensions(data)
    print w, h
    