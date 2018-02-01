#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" A response to http://terse-words.blogspot.com/2011/11/mapreduce-in-python.html """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from multiprocessing import Pool
import random
import string

WORKERS = 10
PROBLEM_SIZE = 1000

def partition(items):
    """Partition the problem into N sub-problems where N = WORKERS."""
    item_count = len(items)
    cut = int(round(item_count / WORKERS + 0.5))
    i = 0
    while i < item_count:
        yield items[i:i+cut]
        i += cut

def map_function(letters):
    """In a single worker, create a sub-solution based on the local data."""
    mapping = defaultdict(lambda: 0)
    for letter in letters:
        mapping[letter] += 1
    return dict(mapping)

def reduce_function(sub_mappings):
    """Reduce all sub-results to a complete result."""
    results = defaultdict(lambda: 0)
    for sub in sub_mappings:
        for letter, count in sub.iteritems():
            results[letter] += count
    return sorted(results.items(), key=lambda t: (-t[1], t[0]))

def main(pool):
    letters = [random.choice(string.uppercase) for i in range(PROBLEM_SIZE)]
    print("raw data:", letters, "\n")

    parts = list(partition(letters))
    print("after partioning:", parts, "\n")

    sub_mappings = pool.map(map_function, parts)
    print("mapped sub-results:", sub_mappings, "\n")

    results = reduce_function(sub_mappings)
    for r in results:
        print("The letter {} appeared {} times".format(*r))

if __name__ == "__main__":
    pool = Pool(processes=WORKERS)
    main(pool)