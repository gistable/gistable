"""
how to count as fast as possible
(numbers from Python 3.5.2 on a Macbook Pro)
YMMV, but these results are pretty stable for me, say +/- 0.1s on repeated runs
"""

from collections import Counter, defaultdict
import random

random_numbers = [random.randrange(10000) for _ in range(10000000)]

# 2.28 s
def use_dict():
    counts = {}
    for x in random_numbers:
        counts[x] = counts.get(x, 0) + 1

# 1.92 s
def use_dict_check():
    counts = {}
    for x in random_numbers:
        if x not in counts:
            counts[x] = 1
        else:
            counts[x] += 1

# 1.51 s
def use_dict_try():
    counts = {}
    for x in random_numbers:
        try:
            counts[x] += 1
        except KeyError:
            counts[x] = 1

# 1.1s
def use_counter_one_shot():
    counts = Counter(random_numbers)

# 4.25s
def use_counter_many_shot():
    counts = Counter()
    for x in random_numbers:
        counts[x] += 1

# 1.49s
def use_defaultdict():
    counts = defaultdict(int)
    for x in random_numbers:
        counts[x] += 1