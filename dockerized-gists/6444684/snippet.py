#!/usr/bin/env python

"""
Git pre-commit hook to enforce PEP8 rules and run unit tests.

Copyright (C) Sarah Mount, 2013.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import re
import subprocess
import sys

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'September 2013'

modified_re = re.compile(r'^[AM]+\s+(?P<name>.*\.py)', re.MULTILINE)


def get_staged_files():
    """Get all files staged for the current commit.
    """
    proc = subprocess.Popen(('git', 'status', '--porcelain'),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, _ = proc.communicate()
    staged_files = modified_re.findall(out)
    return staged_files


def main():
    abort = False
    # Stash un-staged changes.
    subprocess.call(('git', 'stash', '-u', '--keep-index'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,)
    # Determine all files staged for commit.
    staged_files = get_staged_files()
    # Enforce PEP8 conformance.
    print
    print '============ Enforcing PEP8 rules ============='
    for filename in staged_files:
        subprocess.call(('pep8ify', '-w', filename))
        try:
            os.unlink(filename + '.bak')
        except OSError:
            pass
        subprocess.call(('git', 'add', '-u', 'filename'))
    print
    print '========== Checking PEP8 conformance =========='
    for filename in staged_files:
        proc = subprocess.Popen(('pep8', filename),
                                stdout=subprocess.PIPE)
        output, _ = proc.communicate()
        # If pep8 still reports problems then abort this commit.
        if output:
            abort = True
            print
            print '========= Found PEP8 non-conformance =========='
            print output
    # Run unit tests.
    print
    print '============== Running unit tests ============='
    print
    proc = subprocess.Popen(['python', 'pytest.py', 'tests'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, _ = proc.communicate()
    print out
    if 'FAILURES' in out:
        abort = True
    # Un-stash un-staged changes.
    subprocess.call(('git', 'stash', 'pop', '-q'),
                    stdout=subprocess.PIPE)
    # Should we abort this commit?
    if abort:
        print
        print '=============== ABORTING commit ==============='
        sys.exit(1)
    else:
        sys.exit(0)
    return


if __name__ == '__main__':
    main()