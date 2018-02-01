# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import sys


def c(i):
    """
    Simple shell color output function. (Checks if terminal supports color
    before vomitting ANSI codes).

    Usage:

    >>> print c('Some <red>Red</end> and <blue>blue</end> text')
    >>> print c('<green bg>Some green background</end>')
    >>> print c('Some <cyan bold bg>{}</end>').format('interpolation')

    Note: the keyword in the closing tag isn't really relevant, but I like to
    use "</end>" everywhere for shortness and consistency.

    """
    NORMAL, BOLD = (0, 1)
    ESC, RESET = ('\033[{};{}m', '\033[1;m')
    COLORS = {
        'gray': 30, 'grey': 30, 'red': 31, 'green': 32, 'yellow': 33,
        'blue': 34, 'magenta': 35, 'purple': 35, 'cyan': 36, 'white': 37,
    }

    def ansi(m):
        groups = m.groups()
        if not COLORS.get(groups[0].split(' ')[0]):
            print('Unknown color "{}"'.format(groups[0].split(' ')[0]))

        if ' ' in groups[0]:
            color = COLORS.get(groups[0].split(' ')[0])
            weight = 'bold' in groups[0].split(' ') and BOLD or NORMAL
            if 'bg' in groups[0].split(' '):
                color += 10
        else:
            color, weight = COLORS.get(groups[0]), NORMAL
        return ''.join([ESC.format(weight, color), groups[1], RESET])

    def text(m):
        return m.groups()[1]

    return re.sub('<([A-Za-z0-9 ]+|\s+)>(.+?)</(\w+)>',
                    sys.stdout.isatty() and ansi or text, i)