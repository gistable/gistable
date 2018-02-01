#!/usr/bin/env python
import sys, subprocess, collections
from flake8.hooks import git_hook, get_git_param

# `get_git_param` will retrieve configuration from your local git config and
# then fall back to using the environment variables that the hook has always
# supported.
# For example, to set the complexity, you'll need to do:
#   git config flake8.complexity 10
COMPLEXITY = get_git_param('FLAKE8_COMPLEXITY', 10)
STRICT = get_git_param('FLAKE8_STRICT', False)
IGNORE = get_git_param('FLAKE8_IGNORE', None)
LAZY = get_git_param('FLAKE8_LAZY', False)

ExecutionResult = collections.namedtuple(
    'ExecutionResult',
    'status, stdout, stderr'
)

def _execute(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    status = process.poll()
    return ExecutionResult(status, stdout, stderr)

def _current_commit():
    if _execute('git rev-parse --verify HEAD'.split()).status:
        return '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    else:
        return 'HEAD'

def find_auto_migrations():
    """ Returns a list of files about to be commited. """
    diff_index_cmd = 'git diff-index --cached %s' % _current_commit()
    output = _execute(diff_index_cmd.split())
    if not output.status:
        print output.stderr
    results = output.stdout.split('\n')
    has_errors = False
    for result in results:
        if result != '':
            result = result.split()
            if result[4] == 'A' and 'migrations' in result[5] and 'auto' in result[5]:
                has_errors = True
                msg = "= WARNING: Adding migration with auto name! (%s) =" % result[5]
                sep = "-" * len(msg)
                print sep
                print msg
                print sep
    if has_errors:
        sys.exit(1)


if __name__ == '__main__':
    find_auto_migrations()
    sys.exit(git_hook(
        complexity=COMPLEXITY,
        strict=STRICT,
        ignore=IGNORE,
        lazy=LAZY,
    ))