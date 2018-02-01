#!/usr/bin/env python
"""
enable_offline.py - symlink files in your PIP_DOWNLOAD_CACHE so that
``pip install --find-links`` picks them up.

Inspired by http://tartley.com/?p=1423

Usage
-----

1. Use PIP_DOWNLOAD_CACHE to cache your downloads when you're online.

2. If you're offline or an external hosting site is down:

  a) run this script

  b) run: ``pip install --no-index -f $PIP_DOWNLOAD_CACHE ThePackageYouNeed``

3. To clear the symlinks simply run: ``find $PIP_DOWNLOAD_CACHE -type l -delete``
"""
import os
cache_directory = os.environ['PIP_DOWNLOAD_CACHE']
for path, _, files in os.walk(cache_directory):
    for f in files:
        if f.endswith('.content-type'):
            continue
        path_separator = '%2F'
        params_separator = '%3F'
        try:
            last_path_sep = f.rindex(path_separator) + len(path_separator)
        except ValueError:
            # no path separator, not the kind of file we want to symlink.
            continue
        try:
            first_params_sep = f.index(params_separator)
        except ValueError:
            # most of links won't have GET parameters but some providers use
            # them, e.g. SourceForge's `?download`
            first_params_sep = None
        source_path = os.path.join(path, f)
        target_path = os.path.join(path, f[last_path_sep:first_params_sep])
        if not os.path.exists(target_path):
            os.symlink(source_path, target_path)
