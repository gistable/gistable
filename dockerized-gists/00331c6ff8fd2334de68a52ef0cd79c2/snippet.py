#!/usr/bin/env python
"""
Converts Internet Explorer 'capture network traffic' XML to a HAR file.

Turns out that XML is just a HAR file anyways, but in XML form. So this
just converts it to JSON, and Bob's your uncle.

Requires Python 2.7+ and LXML.
"""
from __future__ import unicode_literals

import argparse
import json
from lxml import objectify
import sys


if sys.version_info > (3,):
    str_type = str
else:
    str_type = unicode


list_things = {
    'pages',
    'entries',
    'cookies',
    'queryString',
    'headers',
}


def xml_to_dict(element):
    if element.tag in list_things:
        return [xml_to_dict(e) for e in element.getchildren()]
    else:
        if element.getchildren():
            return {e.tag: xml_to_dict(e) for e in element.getchildren()}
        else:
            return str_type(element.pyval)


def main():
    parser = argparse.ArgumentParser(description="Convert IE's crazy XML-HAR into a real HAR file")
    parser.add_argument('infile', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    tree = objectify.parse(args.infile)
    root = tree.getroot()
    d = {root.tag: xml_to_dict(root)}
    json.dump(d, args.outfile, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
