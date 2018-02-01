#! /usr/bin/env python2
# Requires: PIL, colormath
#
# Improved algorithm now automatically crops the image and uses much 
# better color matching

from PIL import Image, ImageChops
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor
from colormath.color_objects import sRGBColor as RGBColor
from colormath.color_diff import delta_e_cmc as cmc
import argparse
import sys


ANSI_CODES = (
    '\033[00;30m',     # black
    '\033[00;31m',     # red
    '\033[00;32m',     # green
    '\033[00;33m',     # yellow
    '\033[00;34m',     # blue
    '\033[00;35m',     # magenta
    '\033[00;36m',     # cyan
    '\033[00;37m',     # gray
    '\033[01;30m',   # dark gray
    '\033[01;31m',   # bright red
    '\033[01;32m',   # bright green
    '\033[01;33m',   # bright yellow
    '\033[01;34m',   # bright blue
    '\033[01;35m',   # bright magenta
    '\033[01;36m',   # bright cyan
    '\033[01;37m',   # white
)
ANSI_COLORS = (
    RGBColor(0, 0, 0),          # black
    RGBColor(205, 0, 0),        # red
    RGBColor(0, 205, 0),        # green
    RGBColor(205, 205, 0),      # yellow
    RGBColor(0, 0, 238),        # blue
    RGBColor(205, 0, 205),      # magenta
    RGBColor(0, 205, 205),      # cyan
    RGBColor(229, 229, 229),    # gray
    RGBColor(127, 127, 127),    # dark gray
    RGBColor(255, 0, 0),        # bright red
    RGBColor(0, 255, 0),        # bright green
    RGBColor(255, 255, 0),      # bright yellow
    RGBColor(92, 92, 255),      # bright blue
    RGBColor(255, 0, 255),      # bright magenta
    RGBColor(0, 255, 255),      # bright cyan
    RGBColor(255, 255, 255),    # white
)
ANSI_RESET = '\033[0m'
INFINITY = float('inf')


def closest_ansi_color(color):
    # Look up the closest ANSI color
    color = RGBColor(*color[:3])
    closest_dist = INFINITY
    closest_color_index = 0
    for i, c in enumerate(ANSI_COLORS):
        d = color_distance(c, color)
        if d < closest_dist:
            closest_dist = d
            closest_color_index = i
    return ANSI_CODES[closest_color_index]


def color_distance(c1, c2):
    # return a value representing a relative distance between two RGB
    # color values, weighted for human eye sensitivity
    cl1 = convert_color(c1, LabColor)
    cl2 = convert_color(c2, LabColor)
    return cmc(cl1, cl2, pl=1, pc=1)
    # return (math.pow((c2[0] - c1[0]) * 0.30, 2) +
    #         math.pow((c2[1] - c1[1]) * 0.49, 2) +
    #         math.pow((c2[2] - c1[2]) * 0.21, 2))


def convert_image(filename, output_file, fill_char='##'):
    # render an image as ASCII by converting it to RGBA then using the
    # color lookup table to find the closest colors, then filling with 
    # fill_char
    # TODO: use a set of fill characters and choose among them based on
    # color value
    im = Image.open(filename)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # crop the image
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        im = im.crop(bbox)
    w = im.size[0]
    o = ''
    last_color = None
    for i, p in enumerate(im.getdata()):
        if i % w == 0:
            o += '\n'
        if im.mode == 'RGBA' and p[3] == 0:
            o += ' ' * len(fill_char)
        else:
            c = closest_ansi_color(p)
            if last_color != c:
                o += c
                last_color = c
            o += fill_char
    o += ANSI_RESET + '\n\n'
    if output_file is not sys.stdout:
        output_file = open(output_file, 'w')
    output_file.write(o)
    output_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='File to convert to ASCII art')
    parser.add_argument('-o', '--output_file', nargs='?', default=sys.stdout,
                        help='Path to the output file, defaults to stdout')
    parser.add_argument('-f', '--fill_char', nargs='?', default='##',
                        help='Character to use for solid pixels in the image')
    args = parser.parse_args()
    convert_image(args.filename, args.output_file, fill_char=args.fill_char)
