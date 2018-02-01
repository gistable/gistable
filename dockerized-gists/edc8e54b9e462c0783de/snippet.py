#!/usr/bin/env python2
# coding: utf-8
from __future__ import print_function
from tempfile import NamedTemporaryFile
import os
import sys
from shutil import copyfile
from wand.image import Image

DIMENSIONS = {
    'OSX': [
        ('icon_16x16.png',        16),
        ('icon_16x16@2x.png',     16*2),
        ('icon_32x32.png',        32),
        ('icon_32x32@2x.png',     32*2),
        ('icon_128x128.png',      128),
        ('icon_128x128@2x.png',   128*2),
        ('icon_256x256.png',      256),
        ('icon_256x256@2x.png',   256*2),
        ('icon_512x512.png',      512),
        ('icon_512x512@2x.png',   512*2),
    ],
    'IOS': [
        ('icon-29.png',           29),
        ('icon-29@2x.png',        29*2),
        ('icon-40.png',           40),
        ('icon-40@2x.png',        40*2),
        ('icon-40@3x.png',        40*3),
        ('icon-60.png',           60),
        ('icon-60@2x.png',        60*2),
        ('icon-60@3x.png',        60*3),
        ('icon-72.png',           72),
        ('icon-72@2x.png',        72*2),
        ('icon-76.png',           76),
        ('icon-76@2x.png',        76*2),
        ('icon-76@3x.png',        76*3),
        ('icon-512.png',          512),
        ('icon-512@2x.png',       512*2),
        ('icon-small-50.png',     50),
        ('icon-small-50@2x.png',  50*2),
        ('icon-small-50@3x.png',  50*3),
        ('icon-small.png',        29),
        ('icon-small@2x.png',     29*2),
        ('icon-small@3x.png',     29*3),
        ('icon.png',              57),
        ('icon@2x.png',           57*2),
        ('iTunesArtwork.png',     512),
        ('iTunesArtwork@2x.png',  512*2),
    ],
    'ANDROID': [
        ('mipmap-ldpi/ic_launcher.png',     36),
        ('mipmap-mdpi/ic_launcher.png',     48),
        ('mipmap-hdpi/ic_launcher.png',     72),
        ('mipmap-xhdpi/ic_launcher.png',    96),
        ('mipmap-xxhdpi/ic_launcher.png',   144),
        ('mipmap-xxxhdpi/ic_launcher.png',  192),
        ('playstore-icon.png',              512),
    ],
}


cmd = (
    "convert -size {width}x{height} xc:none -fill white -draw "
    "'roundRectangle 0,0 {width},{height} {round_size},{round_size}' "
    "'{round_src_path}' -compose SrcIn -composite '{rounded_path}'")

def create(src_path):
    src_path = os.path.abspath(src_path)

    for t, dims in DIMENSIONS.items():
        for name, size in dims:
            if isinstance(size, int):
                width, height = (size, size)
            else:
                width, height = size

            dest_path = os.path.join('app-icons', t, name)
            dir_path = os.path.dirname(dest_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            with Image(filename=src_path) as src_im:
                src_im.strip()
                src_im.resize(width, height)
                src_im.save(filename=dest_path)

                suffix = os.path.splitext(dest_path)[-1]
                with NamedTemporaryFile(suffix=suffix) as rounded_f:
                    round_size = int(width * 0.15)

                    rounded_path = rounded_f.name
                    current_cmd = cmd.format(**{
                        'width': width,
                        'height': height,
                        'round_size': round_size,
                        'round_src_path': dest_path,
                        'rounded_path': rounded_path,
                    })
                    print(current_cmd)
                    os.system(current_cmd)

                    copyfile(rounded_path, dest_path)

            print('created {}'.format(dest_path))



if __name__ == '__main__':
    try:
        src_path = sys.argv[1]
    except IndexError:
        print('usage> {} <image-path>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    create(src_path)

