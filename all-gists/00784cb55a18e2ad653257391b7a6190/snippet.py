#!/usr/bin/env python
"""Run either pyvenv or virtualenv depending on the version of Python used.

To use this with virtualenvwrappper, install it into a directory on your
``PATH`` as 'virtualenv-select' and add the following to your 
``~/.bashrc``:

    export VIRTUALENVWRAPPER_VIRTUALENV=virtualenv-select

.. note::
    To fix the ``lssitepackages`` and ``cdsitepackages`` commands to work
    with pyvenv-based virtualenvs see:

    https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/167/virtualenvwrapper_get_site_packages_dir-is

"""

import argparse
import subprocess
import sys

GET_VERSION_CMD = 'import sys; sys.stdout.write("%i %i" % sys.version_info[:2])'

parser = argparse.ArgumentParser(prog="virtualenv-select", add_help=False)
parser.add_argument('-p', '--python', metavar='PYTHON_EXE',
                    help='The Python interpreter to use')
parser.add_argument('--extra-search-dir', metavar='DIR', action='append',
                    help='Directory to look for setuptools/pip distributions in')
args, rargs  = parser.parse_known_args(sys.argv[1:])

try:
    py_ver = tuple(int(v) for v in subprocess.check_output(
        [args.python or 'python', '-c', GET_VERSION_CMD]).split())
except subprocess.CalledProcessError:
    py_ver = None

if py_ver and py_ver >= (3, 3):
    virtualenv = 'pyvenv-%i.%i' % py_ver
else:
    virtualenv = 'virtualenv'

    if args.python:
        rargs.insert(0, '--python=%s' % args.python)
    if args.extra_search_dir:
        rargs.extend(['--extra-search-dir=%s' % dir
                      for dir in args.extra_search_dir])

sys.exit(subprocess.call([virtualenv] + rargs))
