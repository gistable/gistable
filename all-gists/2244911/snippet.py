#!/usr/bin/python
#
# Copyright (c) 2012 Dave Pifke.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

# This is a simple performance test of different methods for counting the
# number of occurrences of a series of values.

def values():
    """
    Returns a tuple containing four random values: an integer between 0 and
    512, a boolean, an integer between 0 and 256, and a boolean, respectively.
    """

    from random import randint

    return (randint(0, 512),
            bool(randint(0, 1)),
            randint(0, 256),
            bool(randint(0 , 1)))

def nested_defaultdict(n):
    """
    Returns a series of nested defaultdict objects, four deep.  The value of
    the innermost dict is the number of occurrences of the keys that got us
    there.
    """

    from collections import defaultdict
    from functools import partial

    counts = defaultdict(
        partial(defaultdict,
            partial(defaultdict,
                partial(defaultdict, int))))

    for i in range(n):
        a, b, c, d = values()
        counts[a][b][c][d] += 1

    return counts

def tuple_defaultdict(n):
    """
    Returns a defaultdict where the key is a tuple of the input values and
    the value is the number of occurrences.
    """

    from collections import defaultdict

    counts = defaultdict(int)

    for i in range(n):
        a, b, c, d = values()
        counts[(a, b, c, d)] += 1

    return counts

def namedtuple_defaultdict(n):
    """
    Returns a defaultdict where the key is a namedtuple of the input values and
    the value is the number of occurrences.
    """

    from collections import namedtuple, defaultdict

    counts = defaultdict(int)
    Key = namedtuple('Key', 'a b c d')

    for i in range(n):
        a, b, c, d = values()
        counts[Key(a, b, c, d)] += 1

    return counts

def tuple_counter_update(n):
    """
    Returns a Counter, keyed using a tuple.  Uses Counter.update().
    """

    from collections import Counter

    counts = Counter()

    for i in range(n):
        a, b, c, d = values()
        counts.update((a, b, c, d))

    return counts

def tuple_counter_incr(n):
    """
    Returns a Counter, keyed using a tuple.  Uses Counter()[value] += 1.
    """

    from collections import Counter

    counts = Counter()

    for i in range(n):
        a, b, c, d = values()
        counts[(a, b, c, d)] += 1

    return counts

def namedtuple_counter_update(n):
    """
    Returns a Counter, keyed using a namedtuple.  Uses Counter.update()
    """

    from collections import namedtuple, Counter

    counts = Counter()
    Key = namedtuple('Key', 'a b c d')

    for i in range(n):
        a, b, c, d = values()
        counts.update(Key(a, b, c, d))

    return counts

def namedtuple_counter_incr(n):
    """
    Returns a Counter, keyed using a namedtuple.  Uses Counter()[value] += 1.
    """

    from collections import namedtuple, Counter

    counts = Counter()
    Key = namedtuple('Key', 'a b c d')

    for i in range(n):
        a, b, c, d = values()
        counts[Key(a, b, c, d)] += 1

    return counts

if __name__ == '__main__':
    from timeit import Timer

    funcs = [nested_defaultdict,
             tuple_defaultdict,
             namedtuple_defaultdict,
             tuple_counter_update,
             tuple_counter_incr,
             namedtuple_counter_update,
             namedtuple_counter_incr]

    # Credit to Raymond Hettinger for the following:
    setup = 'from __main__ import %s' % ', '.join([x.__name__ for x in funcs])
    for func in funcs:
        stmt = '%s(%d)' % (func.__name__, 1000)
        print(func.__name__, min(Timer(stmt, setup).repeat(7, 20)))

# eof
