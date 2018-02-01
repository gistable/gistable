#!/usr/bin/env python

import sys
import timing
from pprint import pprint

'''
Recurse elements in passed in string.
'''

class memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}
    def __call__(self, *args):
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]


def recursive_permute(string):
    '''
    Return list of permutations via recursive magic.
    '''
    if len(string) == 1:
        return string
    else:
        res = perm(string)
    return res


@memoize
def perm(string):
    permutations = []
    # iterate over set as to not produce duplicates
    for elem in set(string):
        z = recursive_permute(string.replace(elem, '', 1))

        for t in z:
            permutations.append(elem + t)

    return permutations

def main():
    pprint(recursive_permute(sys.argv[1]))

if __name__ == "__main__":
    main()