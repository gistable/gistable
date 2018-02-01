#!/usr/bin/env python3
# MIT License.
# Copyright (c) 2016 Ramiro Bou (Polsaker)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Usage: img2irc.py image.png [-rgb]
# With -rgb the script uses RGB to compare colors instead of L*A*B*.
# It is faster but it might lead to worse (or better ;D) image quality

from PIL import Image
import numpy as np
import sys, math

if len(sys.argv) == 1:
    print("Usage: img2irc.py image.png [-rgb]")
    sys.exit(1)

image = sys.argv[1]
try:
    rgb = True if sys.argv[2] == "-rgb" else False
except IndexError:
    rgb = False

if not rgb:
    from colormath.color_objects import LabColor, sRGBColor
    from colormath.color_conversions import convert_color


img = Image.open(image).convert('RGBA')
arr = np.array(np.asarray(img).astype('float'))

def distance(c1, c2):
    if rgb:
        (r1,g1,b1) = (c1[0], c1[1], c1[2])
        (r2,g2,b2) = (c2[0], c2[1], c2[2])
    else:
        rgb1 = sRGBColor(c1[0], c1[1], c1[2])
        rgb2 = sRGBColor(c2[0], c2[1], c2[2])
        lab1 = convert_color(rgb1, LabColor)
        lab2 = convert_color(rgb2, LabColor)
        (r1,g1,b1) = lab1.lab_l, lab1.lab_a, lab1.lab_b
        (r2,g2,b2) = lab2.lab_l, lab2.lab_a, lab2.lab_b

    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)

ircColors = {(211, 215, 207): 0,
             (46, 52, 54): 1,
             (52, 101, 164): 2,
             (78, 154, 6): 3,
             (204, 0, 0): 4,
             (143, 57, 2): 5,
             (92, 53, 102): 6,
             (206, 92, 0): 7,
             (196, 160, 0): 8,
             (115, 210, 22): 9,
             (17, 168, 121): 10,
             (88, 161, 157): 11,
             (87, 121, 158): 12,
             (160, 67, 101): 13,
             (85, 87, 83): 14,
             (136, 137, 133): 15}

colors = list(ircColors.keys())

for line in arr:
    row = ""
    for pixel in line:
        if pixel[3] == 0:
            row += "\003  " # \003 to close any potential open color tag
        else:
            closest_colors = sorted(colors, key=lambda color: distance(color, pixel))
            closest_color = closest_colors[0]
            row += "\003{0},{0}  ".format(ircColors[closest_color])
    print(row)
