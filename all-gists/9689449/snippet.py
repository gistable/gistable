#!/usr/bin/env python

import sys

if len(sys.argv[1:]) != 1:
    print "usage: sort_pdb.py <pdb file>"
    sys.exit(1)

try:
    with open(sys.argv[1]) as handle:
        atom_lines = [l.strip() for l in handle if l.startswith(('ATOM', 'HETATM'))]
        sorted_atoms = sorted(atom_lines, key = lambda l: (l[0:6], l[21], int(l[22:26]), l[26], l[16]))
        print '\n'.join(sorted_atoms)
except IOError:
    print "Could not open input file: {0}".format(sys.argv[1])
    sys.exit(1)