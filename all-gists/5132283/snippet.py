#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import argparse
import traceback
import logging

class ArgumentParse(object):
    """
    Parse Argument.

    """
    def __init__(self):
        try:
            parser = argparse.ArgumentParser(description='Command Description')
            parser.add_argument('-f', action="store", dest="file", \
                             help=u"読み込みファイル  defualt=testfile", \
                             default="testfile")
            self.optargs = parser.parse_args()
            self.checkopts()
        except Exception, e:
            print >>sys.stderr, "Argument Parse Error"
            print >>sys.stderr, str(e)
            sys.exit(1)

    def checkopts(self):
        if not self.optargs.file:
            self.opt_messages.append("-f options is required.")
            sys.exit(1)

class Command(object):
    """
    Parent Command Class.

    """
    def __init__(self, argparse):
        self.optargs = argparse

    def run(self):
        pass

class TestCommand(Command):
    """
    Test COmmand Class.

    """
    def run(self):
        print self.optargs.file


def main():
    arguparse = ArgumentParse()
    command = TestCommand(arguparse.optargs)
    command.run()

if __name__ == "__main__":
    main()
