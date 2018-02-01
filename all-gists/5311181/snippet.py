#!/usr/bin/env python

# calculate screen DPI
# supports both python 2 and 3

import re
import argparse
from math import sqrt
from subprocess import check_output

__xlib = False
try:
    # note: Xlib is buggy and prints messages in the stdout
    from Xlib import display
    __xlib = True
except ImportError:
    #print("Cannot load Xlib, falling back to xrandr")
    pass


def cmd_parse():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="DPI calculator")

    parser.add_argument("-r", "--resolution", action="store",
        help="Screen resolution in WxH format")

    parser.add_argument("-a", "--ratio", action="store", default="16:9",
        help="Screen aspect ratio (default: %(default)s)")

    parser.add_argument("-d", "--dimension", action="store", type=float,
        required=True, help="Screen diagonal size (in inches)")

    parser.add_argument("-n", "--normalize", action="store_true", default=False,
        help=("Normalize DPI to reduce scaling artifacts to GUI that use bitmaps"
            " (default: %(default)s)"))

    parser.add_argument("--verbose", action="store_true", default=False,
        help="Show a more detailed result")

    return parser.parse_args()


def _parse_resolution(resolution):
    """Return width and height from a string formatted
       as 'WidthxHeight'"""
    return resolution.split('x')


def _parse_ratio(ratio):
    """Return x and y units from a string formatted as 'X:Y'"""
    x, y = ratio.split(':')
    return float(x), float(y)


def get_resolution_from_X():
    s = display.Display().screen()
    return (s.width_in_pixels, s.height_in_pixels)


def get_resolution_from_xrandr():
    output = check_output('xrandr', universal_newlines=True)
    is_resolution_line = re.compile(r"\*").search
    for line in iter(output.splitlines()):
        if is_resolution_line(line):
            resolution = line.split()[0]
            break

    return _parse_resolution(resolution)


def get_physical_dimensions(diagonal, w, h):
    ratio = w/h
    height = sqrt((diagonal * diagonal) / (1 + ratio * ratio))
    width = height * ratio
    return round(width, 2), round(height, 2)


def calculate_dpi(width, height, p_width, p_height):
    dpi_w = width / p_width
    dpi_h = height / p_height
    return dpi_w, dpi_h


def normalize_dpi(dpi):
    dpi_values = (96, 120, 144, 168, 192)

    new_dpi = dpi
    minimum = 1000
    for dval in dpi_values:
        difference = abs(dval - dpi)
        if difference < minimum:
            minimum = difference
            new_dpi = dval

    return new_dpi


if __xlib:
    get_resolution = get_resolution_from_X
else:
    get_resolution = get_resolution_from_xrandr


if __name__ == "__main__":
    args = cmd_parse()
    if args.resolution:
        width, height = _parse_resolution(args.resolution)
    else:
        width, height = get_resolution()

    x, y = _parse_ratio(args.ratio)
    p_width, p_height = get_physical_dimensions(args.dimension, x, y)


    dpi_w, dpi_h = calculate_dpi(int(width), int(height), p_width, p_height)
    dpi = int(round(dpi_w))

    if args.normalize:
        dpi = normalize_dpi(dpi)

    if args.verbose:
        print("Width: {} Height: {} DPI: {}".format(width, height, dpi))
    else:
        print(dpi)
