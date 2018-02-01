#!/usr/bin/env python

"""
An 8-bit avatar generator.
"""

from __future__ import division

import argparse
import hashlib
import numpy
import png

def chunk(s, n):
    """
    Chunks a string into fragments n characters long.
    """
    for i in range(0, len(s), n):
        yield s[i:i+n]

def map_coords(s, xmax = 4, ymax = 8):
    """
    Transforms two hexadecimal digits (s) to (x, y) coordinates, e.g.,
    
        10 => (1, 0)
        b3 => (1, 3)
        2f => (2, 5)
    
    For values greater than xmax or ymax, use the remainder.
    """
    s = list(s)
    x = s[0]
    y = s[1]
    if x > xmax:
        x = int(x, 16) % xmax
    if y > ymax:
        y = int(y, 16) % ymax
    return (x,y)

def get_coords(md5hash):
    chunked = list(chunk(md5hash, 2))
    coords = []
    for c in chunked:
        coords.append(map_coords(c))
    return list(set(coords))

def choose_foreground(md5hash):
    """
    Placeholder function for something more advanced.
    """
    return pixelize(md5hash[0:6])

def choose_background(md5hash):
    """
    Placeholder function for something more advanced.
    """
    return pixelize(md5hash[6:12])

def colour_distance(rgb1, rgb2):
    """
    Returns the Euclidean distance between two RGB tuples (R, G, B).
    
    Note that this is a first-order estimate; human colour perception is 
    non-Euclidean.
    """
    dR = (rgb1[0] - rgb2[0])
    dG = (rgb1[1] - rgb2[1])
    dB = (rgb1[2] - rgb2[2])
    d = numpy.sqrt(dR**2 + dG**2 + dB**2)
    return d
    
def pixelize(colour):
    """
    Takes a colour in #RRGGBB and returns a pixel value as an RGB tuple.
    """
    components = list(chunk(colour, 2))
    return tuple([int(x, 16) for x in components])

def write_png(arr, filename, palette):
    """
    Write a binary pixel array to a PNG file.
    """
    f = open(filename, 'wb')
    w = png.Writer(palette = palette, bitdepth=1, size=arr.shape)
    w.write(f, arr)
    
def fill_pixel_array(coords, size):
    """
    Construct an avatar pixel array of arbitrary size.
    """
    arr = numpy.zeros((10, 5))
    for c in coords:
        x = c[0]
        y = c[1]
        arr[y+1, x+1] = 1
    arr_mirror = numpy.fliplr(arr)
    arr = numpy.hstack((arr, arr_mirror))
    # Scale the array, e.g. for a scaling factor of n = 2:
    #
    # array([1, 0],     =>  array([1, 1, 0, 0],
    #       [1, 1])               [1, 1, 0, 0],
    #                             [1, 1, 1, 1],
    #                             [1, 1, 1, 1])
    n = size/arr.shape[0]
    arr = numpy.kron(arr, numpy.ones((n, n)))
    return arr

def generate_avatar(md5hash, filename, size):
    """
    Generate an 8-bit avatar from a given MD5 hash.
    """
    fg = choose_foreground(md5hash)
    bg = choose_background(md5hash)
    coords = get_coords(md5hash)
    imgarray = fill_pixel_array(coords, size)    
    write_png(imgarray, filename, [bg, fg])

def main():
    # CLI
    parser = argparse.ArgumentParser(description='Generate a retro avatar.')
    parser.add_argument('email')
    parser.add_argument('--output', default='avatar.png')
    parser.add_argument('--size', default=100, type=int)
    args = parser.parse_args()
    
    email = args.email
    size = args.size
    md5hash = hashlib.md5(email).hexdigest()
    
    generate_avatar(md5hash, args.output, args.size)

if __name__ == '__main__':
    main()
    
