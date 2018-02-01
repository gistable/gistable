#!/usr/bin/python
import os
from itertools import groupby
from shutil import rmtree

from pkg_resources import parse_version


def main():
    """Strips the buildout cache from older egg versions
    """
    cache_dir = os.getenv("HOME") + '/.buildout/eggs'
    eggs = sorted(os.listdir(cache_dir), key=parse_version, reverse=True)
    print "Removing old eggs from buildout cache:"
    for _, g in groupby(eggs, lambda x: x.split('-')[0]):
        g.next() # skip the one with the highest version (or single one)
        for egg in g:
            rmtree(os.path.join(cache_dir, egg))
            print "- %s" % egg

if __name__ == '__main__':
    main()
