#!/usr/bin/env python3

import click
import numpy as np
import sys


class IntOrStr(click.ParamType):
    name = 'int/str'

    def convert(self, value, param, ctx):
        try:
            return int(value)
        except ValueError:
            return value


@click.command()
@click.option('--bins',
              default="fd",
              type=IntOrStr(),
              help="""
                   Number of bins to use, or
                   a binning strategy (fd, sturges, sqrt, etc.)
                   """)
@click.option('--width', default=50, help='Max width for histogram.')
def hist(bins, width):
    data = np.fromiter(sys.stdin.readlines(), np.float)

    h = np.histogram(data, bins=bins)
    scale = max(h[0]) / width

    for i in range(len(h[0])):
        print("{0: 0.2f}".format(h[1][i]), "="*int(h[0][i] // scale))

if __name__ == '__main__':
    hist()