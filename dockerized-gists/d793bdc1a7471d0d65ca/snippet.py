#!/usr/bin/env python3

# Copyright (c) 2014 Joergen Ibsen
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
Example of converting RGB colors from sRGB to Generic RGB.
"""

import math
import operator


# Generated using mkconvmatrix.py
sRGBtoGenericRGB = [[0.9748536, 0.0272905, -0.0021441],
                    [-0.0200038, 1.0542050, -0.0342012],
                    [0.0016914, 0.0015641, 0.9967445]]


def mat_vec_mul(M, v):
    """Multiply matrix by vector."""
    return [sum(map(operator.mul, r, v)) for r in M]


def sRGB_linearize(c):
    if c <= 0.04045:
        return c / 12.92
    else:
        return math.pow((c + 0.055) / 1.055, 2.4)


def GenericRGB_compand(c):
    # Color profile curve for gamma 1.8 is 461 / 256
    return math.pow(max(c, 0.0), 256 / 461.0)


def convert_color(C):
    """Convert color C from sRGB to Generic RGB."""
    C = list(map(sRGB_linearize, C))

    C = mat_vec_mul(sRGBtoGenericRGB, C)

    C = list(map(GenericRGB_compand, C))

    C = [min(max(c, 0.0), 1.0) for c in C]

    return C


if __name__ == '__main__':
    print(convert_color([1.0, 1.0, 1.0]))
    print(convert_color([0.0, 0.0, 0.0]))
    print(convert_color([1.0, 0.0, 0.0]))
    print(convert_color([0.0, 1.0, 0.0]))
    print(convert_color([0.0, 0.0, 1.0]))
