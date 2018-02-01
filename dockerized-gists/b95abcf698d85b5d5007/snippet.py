#!/usr/bin/env python
"""
nbconcat: concatenate notebooks

Usage:

    nbconcat nb1.py nb2.py [nb3.py...] > allmynbs.ipynb

requires IPython >= 3.0
"""

import sys
import IPython

from IPython import nbformat
v = 4

def nbconcat(nbfiles):
    with open(nbfiles[0]) as f:
        nb = nbformat.read(f, as_version=v)
    
    for nbf in nbfiles[1:]:
        with open(nbf) as f:
            nbb = nbformat.read(f, as_version=v)
        nb.cells.extend(nbb.cells)
    
    nbformat.write(nb, sys.stdout)

if __name__ == '__main__':
    nbconcat(sys.argv[1:])
