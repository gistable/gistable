#!/usr/bin/env PYTHONIOENCODING=utf-8 python
# encoding: utf-8
"""Git pre-commit hook which lints Python, JavaScript, SASS and CSS"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import subprocess
import sys

FS_ENCODING = sys.getfilesystemencoding()


def check_linter(cmd, files, **kwargs):
    if not files:
        return
    print('Running %s' % cmd[0])
    return subprocess.check_output(cmd + files, stderr=subprocess.STDOUT, **kwargs).decode(FS_ENCODING)


def filter_ext(extension, files, exclude=None):
    files = [f for f in files if f.endswith(extension)]
    if exclude is not None:
        files = [i for i in files if exclude not in i]
    return files


def lint_files(changed_files):
    changed_files = [i.strip() for i in changed_files.splitlines() if '/external/' not in i]

    changed_extensions = {ext for root, ext in map(os.path.splitext, changed_files)}

    if '.py' in changed_extensions:
        py_files = filter_ext('.py', changed_files)
        check_linter(['frosted'], py_files)
        check_linter(['isort', '-c'], py_files)

    if '.js' in changed_extensions:
        check_linter(['eslint'], filter_ext('.js', changed_files, exclude='.min.'))

    if '.scss' in changed_extensions:
        try:
            check_linter(['scss-lint'], filter_ext('.scss', changed_files))
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 1:
                # scss-lint rc=1 means no message more severe than a warning
                pass
            else:
                raise

    if '.css' in changed_extensions:
        check_linter(['csslint'], filter_ext('.css', changed_files, exclude='.min.'))


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))
    changed_files = subprocess.check_output('git diff --cached --name-only --diff-filter=ACM'.split())
    changed_files = changed_files.decode(FS_ENCODING)

    try:
        lint_files(changed_files)
    except subprocess.CalledProcessError as exc:
        print('Quality check failed:', file=sys.stderr)
        print(' '.join(exc.cmd), file=sys.stderr)
        if exc.output:
            output = exc.output.decode(FS_ENCODING)
            print('\t', '\n\t'.join(output.splitlines()), sep='', file=sys.stderr)
        sys.exit(1)
