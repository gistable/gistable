#!/usr/bin/env python
"""Print symlinks in the $PATH that point to `*.py` files."""
import os

seen = set()
for dirpath in os.environ.get('PATH', '').split(os.pathsep):
    if not os.path.isdir(dirpath): # this follows symlinks
        continue # visit only directories

    # visit "each" directory only once
    p = os.path.realpath(os.path.normcase(dirpath))
    if p in seen:
        continue
    seen.add(p)

    for filename in os.listdir(dirpath):
        path  = os.path.join(dirpath, filename)
        if os.path.islink(path):
            target = os.readlink(path)
            if target.endswith('.py'):
                print("%s -> %s" % (path, target))
