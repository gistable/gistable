#!/usr/bin/env python

# A small modification of enkiv2's code: https://github.com/enkiv2/misc/blob/master/markov2tracery.py

import collections
import json
import re
import sys


def tokenize(s):
    return s.split()


def ngrams(n, tokens):
    return zip(*[tokens[i:] for i in range(n)])


def markov2tracery(s, n):
    grammar = collections.OrderedDict()
    last = "origin"

    words = tokenize(s)
    grams = ngrams(n, words)
    first = True
    for g in grams:
        word = '_'.join(g)
        word = re.sub(r"\W+", "", word).lower()
        key = g[-1] + " #" + word + "#"
        if not (last in grammar):
            if first:
                grammar[last] = [" ".join(g) + " #" + word + "#"]
                first = False
            else:
                grammar[last] = [key]
        else:
            grammar[last].append(key)
        last = word
    if not (last in grammar):
        grammar[last] = [""]
    else:
        grammar[last].append("")

    overdetermined = True
    for k in grammar:
        if len(grammar[k]) > 1:
            overdetermined = False
    if overdetermined:
        sys.stderr.write("Warning: grammar is overdetermined.\n")
    return json.dumps(grammar)


if __name__ == "__main__":
    n = int(sys.argv[1])
    for line in sys.stdin.readlines():
        print(markov2tracery(line, n))
