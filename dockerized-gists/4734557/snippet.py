#! /usr/bin/env python
# coding: utf-8

"""This script reads all .java files from a directory tree and removes unused
import statements. It may have errors in detecting import lines (e.g.  import
lines within block comments, or import lines with another statement in the same
line), and it may have false-negatives when deciding to remove an import (i.e.
it only removes if the last import symbol word doesn't appear at all -
including comments - in the code).

Warning: use it at your own risk. Better have a source control to rollback if
         necessary.
"""
import fnmatch
import re
import sys
import os

#: The regular expression to match a Java import line. It captures the last
#: symbol (i.e. the class name)
IMPORT_RE = re.compile(r'^\s*import\s+[\w\.]+\.(\w+)\s*;\s*(?://.*)?$')


def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

if __name__ == "__main__":

    # locate files in current directory or one specified in command line arg
    root_dir = sys.argv[1] if len(sys.argv) == 2 else os.curdir

    for filename in locate("*.java", root_dir):
        import_lines = {}
        other_lines = []

        # read all lines from file
        with open(filename) as f:
            all_lines = f.readlines()

        for n, line in enumerate(all_lines):
            m = IMPORT_RE.match(line)
            if m:
                # this is an import line, associate the line number with
                # the symbol imported
                import_lines[n] = m.group(1)
            else:
                # this is a non-import line (everything else)
                other_lines.append(line)

        # get the code excluding the import line
        other_code = ''.join(other_lines)

        # now that we got all, let's write only the imports that
        # are found in other_lines (non-import lines)
        with open(filename, 'w') as f:
            for n, line in enumerate(all_lines):
                if (n in import_lines and
                    not re.search(r'(?<!\w)%s(?!\w)' % import_lines[n],
                                  other_code)):
                    # import not found in code... continue (not writing)
                    print "unused: %s at %s:%d" % (line, filename, n)
                    continue
                f.write(line)

    print "Please compile your project to make sure I haven't break anything."