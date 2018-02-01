#!/usr/bin/env python
###############################################################################
# Ryan James

"""
This pre-commit hook runs nosetests and pylint, reporting their scores.
It blocks commits with failing tests.

To install
----------

Place this file in the .git/hooks/ directory of your repo and make it
executable.
"""

from contextlib import contextmanager

from pathlib import Path
from regex import findall, MULTILINE

from clint.textui import puts, indent
from clint.textui.colored import green, red, yellow
from sarge import capture_both, get_stdout, run

MODULE = 'dit'

STASH_INDEX = r'{(.*)}'
FAILED_TESTS = r'(?:errors|failures)=(\d+)'
COVERAGE = r'^TOTAL.*?(\d+)%'
PYLINT_SCORE = r'(\d\d?\.\d\d)/10'

WIDTH = 40
FORMAT = '{{:.<{}}} '.format(WIDTH)

NOSE_CMD = 'nosetests --with-coverage --cover-erase --cover-package={}'

@contextmanager
def stashed():
    """
    Stash and unstash non-indexed changes. This way code that won't be commited
    doesn't effect results.
    """
    run('git stash save -q -u --keep-index "pre-commit"')
    yield
    stashes = get_stdout('git stash list | grep pre-commit')
    index = findall(STASH_INDEX, stashes)
    if index:
        run('git stash pop -q --index={}'.format(index[0]))


def get_test_status():
    """
    Returns the number of test failures and coverage level.
    """
    result = capture_both(NOSE_CMD.format(MODULE))
    output = result.stderr.read()
    if result.returncode != 0:
        failed = sum(map(int, findall(FAILED_TESTS, output, MULTILINE)))
    else:
        failed = 0
    coverage = int(findall(COVERAGE, output, MULTILINE)[0])
    return failed, coverage


def get_pylint_score():
    """
    Returns the pylint score.
    """
    result = get_stdout('pylint {}'.format(MODULE))
    score = findall(PYLINT_SCORE, result)[0]
    return float(score)


def get_color(value):
    """
    Return a color formatter. Red for low, yellow medium and green high.
    """
    color = green if value > 85 else (yellow if value > 60 else red)
    return color


def remove_pyc():
    """
    Remove all *.pyc files.
    """
    path = Path('.')
    for pyc in path.glob('**/*.pyc'):
        pyc.unlink()


def main():
    """
    Stash non-commiting files, run tests and pylint, report results, unstash.
    """
    remove_pyc()

    with stashed():
        with indent(4):
            puts(FORMAT.format('Running tests '), newline=False)
        failures, coverage = get_test_status()
        if failures == 0:
            puts(green('OK'))
        else:
            plural = failures > 1
            puts(red('{} failure{}'.format(failures, 's' if plural else '')))

        with indent(4):
            puts(FORMAT.format('Coverage '), newline=False)
        puts(get_color(coverage)('{}%'.format(coverage)))

        with indent(4):
            puts(FORMAT.format('Running pylint '), newline=False)
        score = get_pylint_score()
        puts(get_color(10*score)('{}'.format(score)))

    remove_pyc()

    if failures != 0:
        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    main()
