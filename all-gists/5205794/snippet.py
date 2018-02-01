#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ready For Python3?

Checks the locally installed distribution for the py3 trove classifier, and if
it's not found, check on PyPI if there's a newer version of this distribution.

This was done with some help from Matrixise.

The result looks like the following:

[...]
django-extended-choices 0.2.1 => NOK, not found on PyPI
twitter 1.9.0 => OK
nosexcover 1.0.7 => NOK, PyPI (1.0.8) => NOK
gorun 1.7 => NOK, PyPI (1.7) => NOK
suds 0.4 => NOK, PyPI (0.4) => NOK
django-tastypie 0.9.11 => NOK, PyPI (0.9.14) => NOK
django-filter 0.5.4 => NOK, PyPI (0.6a1) => NOK
mimeparse 0.1.3 => NOK, PyPI (0.1.4) => OK
urllib3 1.5 => OK
PIL 1.1.7 => NOK, PyPI (1.1.6) => NOK
[...]
40 OK, 8 NOK, 22 OK on PyPI, 74 NOK on PyPI

OK => local distribution says it's compatible
NOK => local distribution doesn't have the py3 trove classifier, and it wasn't found on PyPI
OK on PyPI => the newest version on PyPI says it's compatible
NOK on PyPI => even the newest version on PyPI doesn't have the py3 trove classifier


"""

import pkg_resources
import xmlrpclib

PY3 = 'Python :: 3'

RESULTS = {'local_ok': 0, 'local_nok': 0, 'pypi_ok': 0, 'pypi_nok': 0}

CLIENT = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')


def has_py3(classifiers):
    return [c for c in classifiers if PY3 in c]


for dist in pkg_resources.working_set:
    if has_py3(dist._get_metadata('PKG-INFO')):  # local version is compatible \o/
        print('%s => OK' % dist)
        RESULTS['local_ok'] += 1
    else:  # check on PyPI for a newer version that might support PY3
        name = dist.project_name
        pypi_dist = CLIENT.package_releases(name)
        if pypi_dist:  # a version was found on PyPI
            ver = pypi_dist[0]
            if has_py3(CLIENT.release_data(name, ver)['classifiers']):  # PyPI version compatible
                print('%s => NOK, PyPI (%s) => OK' % (dist, ver))
                RESULTS['pypi_ok'] += 1
            else:  # no luck /o\
                print('%s => NOK, PyPI (%s) => NOK' % (dist, ver))
                RESULTS['pypi_nok'] += 1
        else:  # no luck locally, not found on PyPI /o\
            print('%s => NOK, not found on PyPI' % dist)
            RESULTS['local_nok'] += 1

print('{local_ok} OK, {local_nok} NOK, {pypi_ok} OK on PyPI, '
      '{pypi_nok} NOK on PyPI'.format(**RESULTS))