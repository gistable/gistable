#!/usr/bin/env python

try:
    from pip import get_installed_distributions
except ImportError:
    from sys import exit
    exit("pip not available")

from pkg_resources import parse_version

try:
    from xmlrpclib import ServerProxy
except ImportError:
    from xmlrpc.client import ServerProxy

pypi = ServerProxy("http://pypi.python.org/pypi")

for distribution in sorted(get_installed_distributions(),
        key=lambda distribution: distribution.project_name):
    remote = ''
    project_name = distribution.project_name
    releases = pypi.package_releases(project_name)

    if not releases:
        pypi.package_releases(project_name.capitalize())

    if releases:
        version = parse_version(releases[0])

        if version > distribution.parsed_version:
            remote = "PyPI:{0}=={1}".format(project_name, releases[0])
    else:
        remote = "PyPI:{0} not found".format(project_name)

    local = "{0}=={1}".format(project_name, distribution.version)
    print("{0:40} {1}".format(local, remote))