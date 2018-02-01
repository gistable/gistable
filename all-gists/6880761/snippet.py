#!/usr/bin/env python
import os
import sys
import re
import subprocess
from functools import partial

# Fabric requirement just for easy colour output
from fabric.colors import red, green, yellow


ROOTDIR = CWD = subprocess.check_output('git rev-parse --show-cdup', shell=True).strip() or '.'
if not os.path.isfile(os.path.join(CWD, 'runtests.py')):  # It could be called from submodule
    ROOTDIR = os.path.realpath(os.path.join(CWD, os.path.pardir))


def changed_files():
    for f in subprocess.check_output('git diff --cached --name-only',
                                     cwd=CWD, shell=True).splitlines():
        f = os.path.join(CWD, f)
        if os.path.isfile(f):
            yield f


def _check_ipdb_file(f):
    if not f.endswith('.py'):
        return None  # Don't check non-python files
    s = subprocess.Popen("grep -E -n --with-filename 'import i?pdb' {}".format(f),
                         shell=True, stdout=subprocess.PIPE)
    output = s.communicate()[0]
    if s.returncode == 0:
        return output.strip()
    return None


def check_ipdb(file_list):
    print(green('[pre-commit] Looking for ipdbs...'))
    error_ipdb = 0
    for f in file_list:
        found_ipdb = _check_ipdb_file(f)
        if found_ipdb:
            print(red('> {}'.format(found_ipdb)))
            error_ipdb = 1
    return error_ipdb


def check_flake8_diff():
    print(green('[pre-commit] Checking flake8 for changed lines...'))
    s = subprocess.Popen('git diff --cached | flake8 --diff', shell=True, cwd=CWD,
                         stdout=subprocess.PIPE)
    output = s.communicate()[0]
    if s.returncode:
        for error in output.splitlines():
            error = error.strip()
            if re.search('W\d{3}', error):
                print(yellow(error))
            else:
                print(red(error))
    return s.returncode


def check_tests():
    print(green('[pre-commit] Running unit-tests...'))
    return(subprocess.call('./runtests.py unit --verbosity=0', cwd=ROOTDIR, shell=True))


def main():
    file_list = list(changed_files())
    if not file_list:
        print('Nothing to commit')
        sys.exit(0)
    return_code = check_ipdb(file_list) | check_flake8_diff() | check_tests()
    if return_code:
        print
        print(red('-' * 80))
        print(red('ERRORS FOUND! COMMIT ABORTED.'))
    sys.exit(return_code)


if __name__ == '__main__':
    main()