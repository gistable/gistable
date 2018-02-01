#!/usr/bin/env python

"""
PIP can stand for PIP Installs packages Programmatically, too!
(and here's how)

Requires: 
    * Python 2.6 or higher (for print-as-a-function)
    * PIP 0.8.2
"""

from __future__ import print_function

from pip.index import PackageFinder
from pip.req import InstallRequirement, RequirementSet
from pip.locations import build_prefix, src_prefix

requirement_set = RequirementSet(
    build_dir=build_prefix,
    src_dir=src_prefix,
    download_dir=None)

requirement_set.add_requirement( InstallRequirement.from_line("django-hoptoad", None) )

install_options = []
global_options = []
finder = PackageFinder(find_links=[], index_urls=["http://pypi.python.org/simple/"])

requirement_set.prepare_files(finder, force_root_egg_info=False, bundle=False)
requirement_set.install(install_options, global_options)

print("")
print("Installed")
print("==================================")
[ print(package.name) for package in requirement_set.successfully_installed ]
print("")
