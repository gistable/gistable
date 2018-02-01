#!/usr/bin/python

import compiler
import compiler.ast
import optparse
import sys

class MockChecker(object):
    def __init__(self):
        self.errors = 0
        self.current_filename = ""
        self.non_existent_methods = [
            'assert_calls',
            'assert_not_called',
            'assert_called',
            'assert_called_once',
            'not_called',
            'called_once',
            'called_once_with',
        ]

    def check_files(self, files):
        for file in files:
           self.check_file(file)

    def check_file(self, filename):
        self.current_filename = filename
        try:
            ast = compiler.parseFile(filename)
        except SyntaxError, error:
            print >>sys.stderr, "SyntaxError on file %s:%d" % (filename, error.lineno)
            return
        compiler.walk(ast, self)

    def visitGetattr(self, node):
        if node.attrname in self.non_existent_methods:
            print >>sys.stderr, "%s:%d: you may have called a nonexistent method on mock" % (self.current_filename, node.lineno)
            self.errors += 1

def main():
    parser = optparse.OptionParser(usage="%prog [options] file [files]", description="Checks that the test file does not contain non-existent mock methods")
    (opts, files) = parser.parse_args()
    if len(files) == 0:
        parser.error("No filenames provided")

    checker = MockChecker()
    checker.check_files(files)
    return 1 if checker.errors else 0

if __name__ == '__main__':
    sys.exit(main())