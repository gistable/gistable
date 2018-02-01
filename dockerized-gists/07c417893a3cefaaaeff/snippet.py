#!/usr/bin/env python

"""
This module provides methods to read values from a INI file.
"""

import ConfigParser

class Config(object):

    DEFAULT_SEC = "DEFAULT"

    def __init__(self):
        self.cparser = None

    def read_config(self, config_path):
        self.cparser = ConfigParser.ConfigParser()
        self.cparser.read(config_path)

    def get_val(self, key):
        return self.cparser.get(Config.DEFAULT_SEC, key)

    def get_str(self, key):
        return str(self.get_val(key))

    def get_int(self, key):
        return int(self.get_val(key))

    def get_float(self, key):
        return float(self.get_val(key))


def main():
    print __doc__

if "__main__" == __name__:
    main()