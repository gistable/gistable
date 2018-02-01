# -*- coding:utf-8 -*-
import pip
import xmlrpclib

from fabric.api import task

@task
def pipversions():
    """
    Check installed packeges updates on pypi
    """
    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    for dist in pip.get_installed_distributions():
        available = pypi.package_releases(dist.project_name)
        if not available:
            # Try to capitalize pkg name
            available = pypi.package_releases(dist.project_name.capitalize())
            if not available and '-' in dist.project_name:
                available = pypi.package_releases(dist.project_name.replace('-', '_'))

        if not available:
            msg = 'no releases at pypi'
        elif available[0] != dist.version:
            msg = '{} available'.format(available[0])
        else:
            msg = 'up to date'
        pkg_info = '{dist.project_name} {dist.version}'.format(dist=dist)
        print '{pkg_info:40} {msg}'.format(pkg_info=pkg_info, msg=msg)