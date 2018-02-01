#!/usr/bin/env python
# encoding: utf-8

import imp
import os
import pdb
import pip
import readline
from pip.commands.search import SearchCommand
import sys
import virtualenv

class PyPiPathHook(object):
    def __init__(self):
        # create a virtualenv at ~/.pypi_autoload
        user_home = os.path.expanduser("~")
        self.venv_home = os.path.join(user_home, ".pypi_autoload")
        if not os.path.exists(self.venv_home):
            virtualenv.create_environment(self.venv_home)
        activate_script = os.path.join(self.venv_home, "bin", "activate_this.py")
        execfile(activate_script, dict(__file__=activate_script))

    def find_module(self, fullname, path=None):
        if "." in fullname:
            return None

        try:
            mod = imp.find_module(fullname)
        except ImportError as e:
            pass
        else:
            # it's already accessible, we don't need to do anything
            return None

        if self._package_exists_in_pypi(fullname):
            pip.main(["install", fullname, "--prefix", self.venv_home])

        # we've made it accessible to the normal import procedures
        # now, (should be on sys.path), so we'll return None which
        # will make Python attempt a normal import
        return None

    def _package_exists_in_pypi(self, fullname):
        searcher = SearchCommand()
        options,args = searcher.parse_args([fullname])
        matches = searcher.search(args, options)
        found_match = None
        for match in matches:
            if match["name"] == fullname:
                return True
                break

        return False

sys.meta_path.append(PyPiPathHook())
