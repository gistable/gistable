#!/usr/bin/env python3
# -*- coding: utf-8 -*-


########################################################################################################################
# The MIT License (MIT)
# 
# Copyright (c) 2016 Andrés Correa Casablanca
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
########################################################################################################################


from math import sin, cos, radians
from typing import Sequence, List, Tuple
from random import randint, seed

import colorsys
import numpy
import svgwrite
from time import time


deg60 = radians(60)
cos60, sin60 = cos(deg60), sin(deg60)
cos60n, sin60n = cos(-deg60), sin(-deg60)

rot60 = numpy.array([[cos60, -sin60], [sin60, cos60]])
rot60n = numpy.array([[cos60n, -sin60n], [sin60n, cos60n]])


def generate_chain(level=0, base_chain=['a']):
    if 0 == level:
        return base_chain

    new_chain = []
    for rule in base_chain:
        if rule in ['-', '+']:
            new_chain.append(rule)
        elif 'a' == rule:
            new_chain += ['a', '-', 'b', '-', '-', 'b', '+', 'a', '+', '+', 'a', 'a', '+', 'b', '-']
        elif 'b' == rule:
            new_chain += ['+', 'a', '-', 'b', 'b', '-', '-', 'b', '-', 'a', '+', '+', 'a', '+', 'b']

    return generate_chain(level - 1, new_chain)


def sum_2d_vectors(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    return a[0]+b[0], a[1]+b[1]


def infer_points_from_chain(
    chain: Sequence[str], first_point: Tuple[float, float], segment_size: float
) -> List[Tuple[float, float]]:
    to_right = (segment_size, 0)
    to_left = (-segment_size, 0)

    to_north_east = tuple(rot60.dot(numpy.array(to_right)))
    to_south_east = tuple(rot60n.dot(numpy.array(to_right)))
    to_north_west = tuple(rot60n.dot(numpy.array(to_left)))
    to_south_west = tuple(rot60.dot(numpy.array(to_left)))

    vectors_circle = [to_right, to_north_east, to_north_west, to_left, to_south_west, to_south_east]
    vectors_index = 0
    current_point = first_point

    points = [first_point]
    for step in chain:
        if step in ['a', 'b']:
            current_point = sum_2d_vectors(current_point, vectors_circle[vectors_index])
            points.append(current_point)
        elif '+' == step:
            vectors_index = (vectors_index + 1) % 6
        elif '-' == step:
            vectors_index = (vectors_index - 1) % 6

    return points


def compute_gosper_curve_by_rules(level=4):
    return infer_points_from_chain(
        generate_chain(level),
        (2560.0, 3712.0),
        3072.0 / 7.0**(level*0.5)
    )


def main():
    gosper_points = compute_gosper_curve_by_rules(4)

    svg_document = svgwrite.Drawing(filename="gosperCurve4.svg", size=("4096px", "4096px"))

    n_points = len(gosper_points)
    seed(time())
    hue_index = randint(0, 63)

    for i in range(1, n_points):
        rgb = colorsys.hls_to_rgb(hue_index/64.0, 0.75, 0.75)
        hue_index = (hue_index + randint(0, 1)*2 - 1) % 64

        svg_document.add(
            svg_document.line(
                start=gosper_points[i-1],
                end=gosper_points[i],
                stroke=svgwrite.rgb(rgb[0]*255, rgb[1]*255, rgb[2]*255),
                stroke_width=10,
                stroke_linecap='round',
                fill_opacity=0
            )
        )

    svg_document.save()


if __name__ == "__main__":
    main()

