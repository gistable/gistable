#!/usr/bin/env python

from __future__ import print_function

REQUIREMENTS = [ 'distribute', 'version', 'Cython', 'sortedcollection' ]
try:
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build
    import sortedcollection
except:
    import os, pip
    pip_args = [ '-vvv' ]
    proxy = os.environ['http_proxy']
    if proxy:
        pip_args.append('--proxy')
        pip_args.append(proxy)
    pip_args.append('install')
    for req in REQUIREMENTS:
        pip_args.append( req )
    print('Installing requirements: ' + str(REQUIREMENTS))
    pip.main(initial_args = pip_args)

    # do it again
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build
    import sortedcollection
