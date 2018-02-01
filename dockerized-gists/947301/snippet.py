#!/usr/bin/env python
"""Export CSV from an RRD XML dump.

Usage: rrdxml.py file.xml rra

Where rra is the 0-based index for the RRA you want to dump.

"""
from csv import writer
from itertools import chain, izip
from lxml.etree import parse
from sys import argv, stdout


def comment_content(c):
    """Return the inner content from an XML comment. Strips surrounding
    whitespace.

    >>> comment_content("<!-- Yay! -->")
    'Yay!'

    """
    content = str(c)[4:-3]
    return content.strip()


def get_ts(c):
    """Return the unix timestamp component of an RRD XML date comment.

    >>> get_ts("<!-- 2011-04-28 19:18:40 BST / 1304014720 -->")
    '1304014720'

    """
    date, tstamp = comment_content(c).split("/")
    return tstamp.strip()


def iunshift(i1, i2):
    """Take one iterator of values and one iterator of iterators and return an
    iterator of iterators with the values prepended.

    >>> l = iunshift([1, 2, 3], [[2, 3], [3, 4], [4, 5]])
    >>> [list(e) for e in l]
    [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    """
    for x in izip(i1, i2):
        yield chain([x[0]], x[1])


def headers(tree):
    return (s.strip() for s in tree.xpath("//ds/name/text()"))


def values(tree, rra_index):
    row_nodes = tree.xpath("//rra[%s]/database/row" % rra_index)
    for rn in row_nodes:
        yield (v.text for v in rn)


def timestamps(tree, rra_index):
    """Extract timestamps from comments."""
    timestamp_nodes = tree.xpath("//rra[%s]/database/comment()" % rra_index)
    return (get_ts(c) for c in timestamp_nodes)


def rows(tree, rra_index):
    return iunshift(timestamps(tree, rra_index), values(tree, rra_index))


def dump(f, rra):
    """Dump RRA to list of lists."""
    tree = parse(f)
    yield headers(tree)
    for row in rows(tree, rra + 1):
        yield row


def dump_csv(f, rra, out):
    """Dump RRA to CSV (written to file object out)."""
    w = writer(out)
    for row in dump(f, rra):
        w.writerow([s.strip() for s in row])


if __name__ == "__main__":
    dump_csv(argv[1], int(argv[2]), stdout)
