#!/usr/bin/env python2
# coding: utf8
# GistID: 8446782

import hashlib
import os
import sys


def get_size(path):
    st = os.stat(path)
    return st.st_size


def main():
    sizes = set()
    hashes = {}
    dups = {}
    path = sys.argv if sys.argv[1:] else '.'
    for dirs, _, flist in os.walk(path):
        for f in flist:
            path = os.path.join(dirs, f)
            size = get_size(path)
            if size in sizes:
                with open(path) as fin:
                    hsh = hashlib.md5(fin.read()).hexdigest()
                    hashes.setdefault(hsh, []).append(path)
            sizes.add(size)

    dups = [v for v in hashes.values() if len(v) > 1]
    for d in dups:
        for p in d:
            print p
        print

if __name__ == '__main__':
    main()