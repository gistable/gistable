"""IPython startup script to detect and inject VIRTUAL_ENV's site-packages dirs.

IPython can detect virtualenv's path and injects it's site-packages dirs into sys.path.
But it can go wrong if IPython's python version differs from VIRTUAL_ENV's.

This module fixes it looking for the actual directories. We use only old stdlib
resources so it can work with as many Python versions as possible.

References:
http://stackoverflow.com/a/30650831/443564
http://stackoverflow.com/questions/122327/how-do-i-find-the-location-of-my-python-site-packages-directory
https://github.com/ipython/ipython/blob/master/IPython/core/interactiveshell.py#L676

Author: Henrique Bastos <henrique@bastos.net>
License: BSD
"""
import os
import sys
from warnings import warn


virtualenv = os.environ.get('VIRTUAL_ENV')

if virtualenv:

    version = os.listdir(os.path.join(virtualenv, 'lib'))[0]
    site_packages = os.path.join(virtualenv, 'lib', version, 'site-packages')
    lib_dynload = os.path.join(virtualenv, 'lib', version, 'lib-dynload')

    if not (os.path.exists(site_packages) and os.path.exists(lib_dynload)):
        msg = 'Virtualenv site-packages discovery went wrong for %r' % repr([site_packages, lib_dynload])
        warn(msg)

    try:
        i = sys.path.index("") + 1
    except ValueError:
        i = 0
    sys.path.insert(i, site_packages)
    sys.path.insert(i+1, lib_dynload)