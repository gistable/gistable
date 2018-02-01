#!/usr/bin/env python
"""
ignore_moves.py v0.2
Filter relocated lines from a unified diff format stream.
Offered under the terms of the MIT License at github.com
Taken from http://stackoverflow.com/questions/1380333/
"""

import sys
from optparse import OptionParser

RED = 31
GREEN = 32

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[0;%dm"


def inverse(line):
    """
    Swap a delta line between + and -
    """
    return ('-' if line[0] == '+' else '+') + line[1:].strip()


def reverse_enumerate(lst):
    """
    A handy generator
    """
    for index, value in enumerate(reversed(lst)):
        yield len(lst) - 1 - index, value


def dumpchanges(stack, options):
    """
    Redender output. Called for each disparate file in the diff.
    """
    for line in stack:
        if options.plain:
            print line.strip()
        else:
            seq = COLOR_SEQ % (GREEN if line.startswith('+') else RED)
            print seq + line.strip() + RESET_SEQ
    stack[:] = []


def main():
    """
    The primary logic
    """
    parser = OptionParser(usage="usage: cat diff.patch | %prog [-p]",
      description="Filter relocated lines from a unified diff format stream.",
      version="%prog 0.2",
      epilog="Offered under the terms of the MIT License at github.com")
    parser.add_option("-p", "--plain", action="store_true", dest="plain",
      default=False, help="don't highlight output")
    options = parser.parse_args()[0]
    stack = []

    for line in sys.stdin.readlines():
        if not line[1:].strip():
            continue  # ignore empty lines
        if line.startswith(('---', '+++')):
            dumpchanges(stack, options)
            print line.strip()
        elif line.startswith(('+', '-')):
            inverted = inverse(line)
            line = line[0] + line[1:].strip()
            for i, match in reverse_enumerate(stack):
                if inverted == match:
                    stack.pop(i)
                    break
            else:
                stack.append(line)

    # finished reading, still have state to be dumped
    dumpchanges(stack, options)


main()
