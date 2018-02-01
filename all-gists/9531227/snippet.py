#!/usr/bin/env python
# coding=utf-8
"""
Colors
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import collections
Colors = collections.namedtuple('Colors', [
    "LIGHT_PINK", "LIGHT_BROWN", "LIGHT_PURPLE", "LIGHT_ORANGE",
    "LIGHT_BLUE", "LIGHT_GREEN", "LIGHT_RED", "LIGHT_BLACK",
    "MIDDLE_PINK", "MIDDLE_BROWN", "MIDDLE_PURPLE", "MIDDLE_ORANGE",
    "MIDLE_BLUE", "MIDDLE_GREEN", "MIDDLE_RED", "MIDDLE_BLACK",
    "DARK_PINK", "DARK_BROWN", "DARK_PURPLE", "DARK_ORANGE",
    "DARK_BLUE", "DARK_GREEN", "DARK_RED", "DARK_BLACK",
])
COLORS = Colors(
    "#EBBFD9", "#DDB8A9", "#D4B2D3", "#F2D1B0",
    "#B8D2EB", "#D8E4AA", "#F2AEAC", "#CCCCCC",
    "#D77FB3", "#CD7058", "#9E66AB", "#F9A65A",
    "#599AD3", "#79C36A", "#F1595F", "#727272",
    "#B33893", "#A11D20", "#662C91", "#F37D22",
    "#1859A9", "#008C47", "#ED2D2E", "#010101",
)

if __name__ == '__main__':
    print "<ul>"
    for name, color in COLORS._asdict().items():
        print "<li style='color: %s'>%s (%s)" % (color, name, color)
   print "</ul>"