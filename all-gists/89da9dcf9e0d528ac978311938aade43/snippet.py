#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2017 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Small delegating Python script to allow multiple hooks in a git repository.

Usage:

Make your building system to create a symbolic link in the git hooks directory
to this script with the name of the hook you want to attend. For example,
``pre-commit``.

This hook will then execute, in alphabetic order, all executables files
(subhooks) found under a folder named after the hook type you're attending
suffixed with ``.d``. For example, ``pre-commit.d``.

For example:

```
.git/hooks/
|_ pre-commit
|_ pre-commit.d/
   |_ 01-cpp_coding_standard
   |_ 02-python_coding_standard
   |_ 03-something_else
```

Additionally, colored logging is supported if the package colorlog is 
installed.
"""

from sys import argv
from logging import getLogger
from subprocess import Popen, PIPE
from os import access, listdir, X_OK
from os.path import isfile, isdir, abspath, normpath, dirname, join, basename


GIT_HOOKS = [
    'applypatch-msg',
    'commit-msg',
    'post-update',
    'pre-applypatch',
    'pre-commit',
    'prepare-commit-msg',
    'pre-push',
    'pre-rebase',
    'update',
]


def setup_logging():
    """
    Setup logging with support for colored output if available.
    """

    from logging import basicConfig, DEBUG

    FORMAT = (
        '  %(log_color)s%(levelname)-8s%(reset)s | '
        '%(log_color)s%(message)s%(reset)s'
    )

    logging_kwargs = {
        'level': DEBUG,
    }

    try:
        from logging import StreamHandler
        from colorlog import ColoredFormatter

        stream = StreamHandler()
        stream.setFormatter(ColoredFormatter(FORMAT))

        logging_kwargs['handlers'] = [stream]

    except ImportError:
        pass

    basicConfig(**logging_kwargs)


def main():
    """
    Execute subhooks for the assigned hook type.
    """
    setup_logging()
    log = getLogger(basename(__file__))

    # Check multihooks facing what hook type
    hook_type = basename(__file__)
    if hook_type not in GIT_HOOKS:
        log.fatal('Unknown hook type: {}'.format(hook_type))
        exit(1)

    # Lookup for sub-hooks directory
    root = normpath(abspath(dirname(__file__)))
    hooks_dir = join(root, '{}.d'.format(hook_type))
    if not isdir(hooks_dir):
        log.warning('No such directory: {}'.format(hooks_dir))
        exit(0)

    # Gather scripts to call
    files = [join(hooks_dir, f) for f in listdir(hooks_dir)]
    hooks = sorted(
        [h for h in files if isfile(h) and access(h, X_OK)]
    )
    if not hooks:
        log.warning('No sub-hooks found for {}.'.format(hook_type))
        exit(0)

    # Execute hooks
    for h in hooks:
        hook_id = '{}.d/{}'.format(hook_type, basename(h))
        log.info('Running hook {}...'.format(hook_id))

        proc = Popen([h] + argv[1:], stdout=PIPE, stderr=PIPE)
        stdout_raw, stderr_raw = proc.communicate()

        stdout = stdout_raw.decode('utf-8').strip()
        stderr = stderr_raw.decode('utf-8').strip()

        if stdout:
            log.info(stdout)
        if stderr:
            log.error(stderr)

        # Log errors if a hook failed
        if proc.returncode != 0:
            log.error('Hook {} failed. Aborting...'.format(hook_id))
            exit(proc.returncode)


if __name__ == '__main__':
    main()
