#!/usr/bin/env python

"""
Build wheels of all currently installed packages (as listed by "pip freeze")
"""

import glob
import importlib
from subprocess import call

__license__ = 'MIT'
__copyright__ = '2013, Kwarter'


def make_version_tuple(version_string):
    """
    This is less intelligent than pip.commands.search.compare_versions,
    but we might not have pip available yet. This is Good Enough for this
    limited purpose.
    """
    return [int(_) for _ in version_string.split('.')]


def install(name, version):
    """
    Install one of the prerequisites. Try to use pip first, but it may not
    be installed or may be broken. Fall back to easy_install if that
    happens.
    """
    req = '%s==%s' % (name, version)
    if call(['pip', 'install', '--upgrade', req]):
        call(['easy_install', req])


def bootstrap():
    """
    Ensure that sufficiently recent versions of all necessary tools are
    installed.
    """
    reqs = [
        ('setuptools', '1.1'),
        ('pip', '1.4'),
        ('wheel', '0.21.0'),
    ]
    for module_name, needed_version in reqs:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            install(module_name, needed_version)
        if make_version_tuple(module.__version__) < make_version_tuple(needed_version):
            install(module_name, needed_version)


def make_wheels():
    """Build wheels of all installed packages that don't already have one"""
    bootstrap()

    from pip import get_installed_distributions
    from pip.wheel import Wheel
    from wheel.install import WheelFile
    from wheel.util import matches_requirement

    supported_wheels = []
    for wheel_file in glob.glob('/tmp/wheelhouse/*.whl'):
        wheelobj = Wheel(wheel_file)
        if wheelobj.supported():
            supported_wheels.append(WheelFile(wheel_file))

    for dist in get_installed_distributions():
        if dist.project_name == 'kwarter':
            continue

        distid = '{0.project_name}=={0.version}'.format(dist)
        if not matches_requirement(distid, supported_wheels):
            call(['pip', 'wheel', '-w', '/tmp/wheelhouse', '--no-deps', distid])


if __name__ == '__main__':
    make_wheels()
