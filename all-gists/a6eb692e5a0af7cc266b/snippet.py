#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script creates ground control points (GCPs) from naviigation files for
the GOES images.

The navigation files can be obtained from a web site hosted by the NASA Goddard
Flight Center (GSFC):

    http://goes.gsfc.nasa.gov/goeswest/ or
    http://goes.gsfc.nasa.gov/goeseast/


Usage
-----

The GSFC site provides several versions of navigation files. They are either
formatted as 4-byte float or 2-byte integer, and each is either encoded in MSBF
or LSBF byte order.  Download a file with the name ending with
"*_L_float.nav.gz".  The file is formatted as 4-byte float and encoded in LSBF
byte order.

Run this script:

    $ ./create_ground_control_points.py conus_0801031800_G11I04_L_float.nav.gz

This will print the GCPs in STDOUT.  Note that this script assumes that input
navigation file has the name ending with "*_L_float.nav.gz".
"""
from __future__ import division

import argparse
import gzip
import os
import random
import re
import struct


CONFIG = {
    'conus_G13I04': {  # GOES-EAST
        'image_size': (1200, 1000),   # (w, h)
        'bbox': (20, 320, 610, 420),  # (x, y, w, h)
    },
    'conus_G11I04': {  # GOES-WEST
        'image_size': (1200, 1000),
        'bbox': (600, 320, 540, 420),
    },
    'colorado_G13I04': {  # GOES-EAST
        'image_size': (300, 250),
        'bbox': (0, 0, 299, 249),
    },
    'colorado_G11I04': {  # GOES-WEST
        'image_size': (171, 250),
        'bbox': (0, 0, 170, 249),
    },
}

ELEMSIZE = 4
NUM_SAMPLES = 300


def _generate_sample_points(num_samples, img_size, bbox):
    randint = random.randint

    x0, y0, w, h = bbox
    pts = []
    while True:
        x = randint(x0, x0 + w)
        y = randint(y0, y0 + h)
        idx = x + y * img_size[0]
        if idx in pts:
            continue
        else:
            pts.append(idx)
        if len(pts) > num_samples:
            break
    pts.sort()
    return pts


def _get_config_key(filename):
    bname = os.path.basename(filename)
    regionid = bname.split('_')[0]
    goesid = re.search(r'G\d{2}', bname).group()
    return regionid + '_' + goesid + 'I04'


def create_ground_control_points(filename, num_samples):
    if not filename.endswith('_L_float.nav.gz'):
        raise ValueError("filename must ends with '_L_float.nav.gz'")

    size = 2 * ELEMSIZE

    config = CONFIG[_get_config_key(filename)]
    img_size, bbox = config['image_size'], config['bbox']

    sample_pts = _generate_sample_points(num_samples, img_size, bbox)

    fd = gzip.open(filename, 'rb')
    gcps = []
    for idx in sample_pts:
        fd.seek(size * idx)
        lat, lon = struct.unpack('<2f', fd.read(size))
        y, x = divmod(idx, img_size[0])
        gcps.append([x, y, lon, lat])
    fd.close()
    return gcps


def main(args):
    filename = args.navfile
    gcps = create_ground_control_points(filename, args.num_samples)

    for l in gcps:
        print('{0[0]:4d} {0[1]:4d} {0[2]:13.8f} {0[3]:12.8f}'.format(l))


def init_argparser(parser):
    parser.set_defaults(func=main)
    # Positional arguments
    parser.add_argument('navfile',
                        metavar='input',
                        help="navigation file")
    parser.add_argument('-n', '--num_samples', type=int,
                        default=NUM_SAMPLES,
                        metavar='num',
                        help="number of samples")
    return parser


if __name__ == '__main__':
    parser = init_argparser(argparse.ArgumentParser())

    args = parser.parse_args()
    args.func(args)