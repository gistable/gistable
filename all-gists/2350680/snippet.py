#!/usr/bin/python
"""Convert CSV table to MindMap format

Usage: python csv_to_mm.py sometable.csv > mymap.mm

CSV format is rows representing tree leaves, e.g.:
    A1,
    A1,B1
    A1,B1,C1
    A1,B1,C2
    A2,B2

Parses into the following tree:
    A1
      B1
        C1
        C2
    A2
      B2

"""

# http://pypi.python.org/pypi/xmlbuilder
from xmlbuilder import XMLBuilder
import csv
import sys


def csv_to_tree(rows):
    root = {}
    for row in rows:
        tree = root
        for val in row:
            if val == '':
                break
            if val not in tree:
                tree[val] = {}
            tree = tree[val]
    return root


def tree_to_xml(root):
    xml = XMLBuilder('map', version='0.9.0')

    def rec_tree(tree, xnode):
        if tree == {}:
            return
        xnode['folded'] = 'true'
        for key, subtree in tree.iteritems():
            rec_tree(subtree, xnode.node(text=key))
    xroot = xml.node(text='Categories')
    rec_tree(root, xroot)
    xroot['folded'] = 'false'
    return str(xml)


def csv_to_mm_file(inpath):
    with open(inpath) as instream:
        rows = [[v.decode('utf-8') for v in row]
                for row in csv.reader(instream)]
        print tree_to_xml(csv_to_tree(rows))


if __name__ == "__main__":
    csv_to_mm_file(sys.argv[1])
