#!/usr/bin/env python
# coding: UTF-8

import cv2
import numpy as np


def make_lut256x16(exportPath):
    ''' 256 x 16 LUT '''
    colors = []
    for y in range(0, 16):
        rows = []
        for x in range(0, 256):
            rows.append([
                (x / 16) * 16,  # blue
                y * 16,  # green
                (x % 16) * 16  # red
            ])
        colors.append(rows)

    image = np.array(colors)
    if exportPath:
        cv2.imwrite(exportPath, image)
    return image


def make_lut1024x32(exportPath):
    ''' 1024 x 32 LUT '''
    colors = []
    for y in range(0, 32):
        rows = []
        for x in range(0, 1024):
            rows.append([
                (x / 32) * 8,  # blue
                y * 8,  # green
                (x % 32) * 8  # red
            ])
        colors.append(rows)

    image = np.array(colors)
    if exportPath:
        cv2.imwrite(exportPath, image)
    return image


def make_lut512x512(exportPath):
    ''' 512 x 512 Basic LUT '''
    colors = []
    for y in range(0, 512):
        rows = []
        for x in range(0, 512):
            i = (x % 64, y % 64)
            rows.append([  # BGR
                (y / 2 + x / 16),  # blue
                i[1] * 4,  # green
                i[0] * 4  # red
            ])
        colors.append(rows)

    image = np.array(colors)
    if exportPath:
        cv2.imwrite(exportPath, image)
    return image


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='LUT Texture maker')
    parser.add_argument('path',
                        type=str,
                        nargs='?',
                        default='lut.png',
                        help='output filename')
    parser.add_argument('-s', '--size',
                        type=str,
                        nargs='?',
                        default='512x512',
                        help='256x16 or 1024x32 or 512x512')
    args = parser.parse_args()
    if args.size == '512x512':
        make_lut512x512(args.path)
    elif args.size == '256x16':
        make_lut256x16(args.path)
    elif args.size == '1024x32':
        make_lut1024x32(args.path)
    else:
        sys.exit('Unsupported size')
