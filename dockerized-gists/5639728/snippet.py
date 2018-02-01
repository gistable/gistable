#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pycache -- cache a python package from PyPI on S3.

A simple script to collect a cache of packages locally and sync them up to an S3 bucket, using directories as namespaces so that different projects can have different dependencies.

This is just about the simplest thing that could possibly work.
"""
import warnings
warnings.filterwarnings('ignore')

import os
import argparse
import itertools

from paver.easy import path
from pip.req import parse_requirements
from setuptools.package_index import PackageIndex

__cache__ = path("~/.pycache").expanduser().abspath()
if not __cache__.exists():
    __cache__.makedirs()

index = PackageIndex(index_url="http://pypi.python.org/simple/", search_path=[])

html = """<html>
<head><title>Index - {project}</title></head>
<body>
<h1>{project}</h1>
{body}
</body>
</html>
"""


def main(requirements):

    if not __cache__.exists():
        __cache__.makedirs()

    for line in parse_requirements(requirements):
        package = str(line.req)
        if line.req is None:
            continue
        tmp = path(os.tmpnam())
        if not tmp.exists():
            tmp.makedirs()
        dl = index.download(package, tmp)
        if dl is not None:
            fn = path(dl)
            fn.copy(__cache__ / fn.name)
            for fn in tmp.listdir():
                fn.remove()
            tmp.removedirs()

    build_index(__cache__)


def build_index(cache_dir):
    for __cache__ in itertools.chain((cache_dir, ), cache_dir.walkdirs()):
        links = ('<li><a href="{project}/{file}">{name}</a></li>'.format(
            project=cache_dir.partition(cache_dir)[-1],
            file=fn.isdir() and (fn.name + '/index.html') or fn.name,
            name=fn.name
        ) for fn in cache_dir.listdir() if fn.name != 'index.html')

        with open((cache_dir / 'index.html'), 'w') as fo:
            fo.write(html.format(body="<ul>%s</ul>" % ''.join(links),
                                 project=cache_dir.name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cache a python package from PyPI.')
    parser.add_argument('-r', '--requirements', action='store', default="requirements.txt")
    args = parser.parse_args()
    main(args.requirements)
