#!/usr/bin/env python
# -*- coding: utf-8 -*-

# INSTRUCTIONS:
#
# 1) Install graphviz (http://www.graphviz.org)
# 2) Run on terminal:
#       python graph_coloring.py | dot -Tpng -o graph.png
#    or, if you have imagemagick installed:
#       python graph_coloring.py | dot -Tpng | display

from __future__ import print_function
import random


PALETTE = ('#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462',
           '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5', '#ffed6f')

SOUTH_AMERICA_GRAPH = {
    'Brasil': ['Uruguay', 'Argentina', 'Paraguay', 'Bolivia', 'Peru',
               'Colombia', 'Venezuela', 'Guyana', 'Suriname', 'French Guiana'],
    'Uruguay': ['Brasil', 'Argentina'],
    'Argentina': ['Chile', 'Bolivia', 'Paraguay', 'Brasil', 'Uruguay'],
    'Chile': ['Peru', 'Bolivia', 'Argentina'],
    'Bolivia': ['Argentina', 'Paraguay', 'Brasil', 'Peru', 'Chile'],
    'Colombia': ['Venezuela', 'Brasil', 'Peru', 'Ecuador'],
    'Peru': ['Ecuador', 'Colombia', 'Brasil', 'Bolivia', 'Chile'],
    'Ecuador': ['Colombia', 'Peru'],
    'Venezuela': ['Guyana', 'Brasil', 'Colombia'],
    'Paraguay': ['Brasil', 'Argentina', 'Bolivia'],
    'Guyana': ['Suriname', 'Brasil', 'Venezuela'],
    'Suriname': ['French Guiana', 'Brasil', 'Guyana'],
    'French Guiana': ['Brasil', 'Suriname'],
}


def generate_dot(graph, colors=None, palette=PALETTE):
    assert len(set(colors.values())) <= len(palette), (
        "Too few colors in the palette")

    edges = []
    for node, adjacents in graph.items():
        for n in adjacents:
            if not ((node, n) in edges or (n, node) in edges):
                edges.append((node, n))

    result = 'graph {\n'
    result += ''.join('    "{}" -- "{}";\n'.format(*e) for e in edges)

    if colors:
        style = '    "{}" [style="filled",fillcolor="{}",shape=box];\n'
        result += ''.join(style.format(node, palette[color])
                          for node, color in colors.items())
    result += '}\n'

    return result


def try_coloring(graph, num_colors):
    """Try coloring a graph using given maximum number of colors
    >>> grafo = {
    ...     'A': ['B', 'C'],
    ...     'B': ['A'],
    ...     'C': ['A'],
    ... }
    >>> try_coloring(grafo, 1)
    >>> try_coloring(grafo, 2)
    {'A': 0, 'C': 1, 'B': 1}
    """
    assert num_colors > 0, "Invalid number of colors: %s" % num_colors
    colors = {}

    def neighbors_have_different_colors(nodes, color):
        return all(color != colors.get(n) for n in nodes)

    for node, adjacents in graph.items():

        found_color = False

        for color in range(num_colors):
            if neighbors_have_different_colors(adjacents, color):
                found_color = True
                colors[node] = color
                break

        if not found_color:
            return None

    return colors


def find_graph_colors(graph):
    for num_colors in range(1, len(graph)):
        colors = try_coloring(graph, num_colors)
        if colors:
            return colors


def get_random_palette():
    random_palette = list(PALETTE)
    random.shuffle(random_palette)
    return random_palette


if __name__ == '__main__':
    graph = SOUTH_AMERICA_GRAPH

    colors = find_graph_colors(graph)

    # random palette just for fun
    palette = get_random_palette()

    print(generate_dot(graph, colors, palette))
