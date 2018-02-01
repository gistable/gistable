#!/usr/bin/env python
"""
This script checks whether a name is taken on PyPI.

Usage:

    onpypi fakename requests

Prints:

    fakename  False
    requests  True

Indicating that the name "fakename" is available on PyPI.

"""

from __future__ import print_function

import argparse
import sys
from collections import namedtuple

import requests

URL = 'https://pypi.python.org/pypi/{}'
Check = namedtuple('Check', ['name', 'taken'])


def taken(name):
    res = requests.head(URL.format(name))
    return res.ok


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'Check whether names are taken on PyPI. '
            'False means the name is available.'))
    parser.add_argument('names', nargs='+', help='Names to check')
    return parser.parse_args()


def print_checks(checks):
    max_len = max(len(c.name) for c in checks)
    tpl = '{{:{}}}  {{}}'.format(max_len)

    for c in checks:
        print(tpl.format(*c))


def main():
    args = parse_args()
    print_checks([Check(name, taken(name)) for name in args.names])


if __name__ == '__main__':
    sys.exit(main())
