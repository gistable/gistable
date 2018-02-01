#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Usage: %prog [width [columns]] < table.csv

Pretty-print CSV file with fixed width columns.

Arguments:

  width    maximum width of the column, long text is truncated
  columns  coma-separated numbers or ranges, like "1,2,6-8";
           column numbering starts from 1.
"""

import csv
from sys import argv, stdin
from os.path import basename

def u(s):
    return unicode(s, "utf-8")

def truncate(s, width):
    if len(s) < width:
        return s
    else:
        return s[:(width-1)] + u"…"

def main():
    w = int(argv[1]) if len(argv) > 1 else 10
    cols = argv[2] if len(argv) > 2 else "1-9999"
    cols = [ tuple(map(int,rng.split("-")[:2]))
             if "-" in rng
             else int(rng)
             for rng in cols.split(",") ]
    r = csv.reader(stdin)
    for ln in r:
        ranges = [ ln[rng[0]-1:rng[1]] if type(rng) == tuple else [ln[rng-1]]
                   for rng in cols ]
        fields = [ fld for rng in ranges for fld in rng ]  # concat
        print " ".join([ "%*s" % (w, truncate(u(fld),w)) for
                         fld in fields ])

def usage():
    print __doc__.replace("%prog", basename(argv[0]))

if __name__ == "__main__":
    if "--help" in argv or "-h" in argv:
        usage()
    else:
        main()
