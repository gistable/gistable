#!/usr/bin/env python3

'''
Find the full import chain from one go package to another.

Usage:
    import-finder.py source_package target_package

This is useful in large codebases to figure out why, for example, the testing package is
included in a resulting binary.
'''

import collections
import subprocess
import sys
import functools

@functools.lru_cache(maxsize=10000)
def list_imports(package):
    if package == 'C':
        return ()
    out = subprocess.check_output(['go', 'list', '-f', '{{range .Imports}}{{.}} {{end}}', package])
    imports = out.decode('utf-8').split()
    return tuple(filter(lambda x: x != '', imports))

nomatch = {}

def find_import_chain(start, end):
    if start in nomatch:
        return None
    print("Searching for %s → %s..." % (start, end), file=sys.stderr)
    if start == end:
        return collections.deque([start])
    imports = list_imports(start)
    for x in imports:
        chain = find_import_chain(x, end)
        if chain is not None:
            chain.appendleft(start)
            return chain
    else:
        nomatch[start] = True

def main():
    chain = find_import_chain(sys.argv[1], sys.argv[2])
    if chain is not None:
        print(' → '.join(chain))

if __name__ == "__main__":
    main()
