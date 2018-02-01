####################################
# Copyright Christopher Abiad, 2013
# All Rights Reserved
####################################
"""In-place quicksorting."""

__author__ = 'Christopher Abiad'

from random import randrange

def _partition(l, low, high):
    """Partition the list using a random element as the pivot.

    NOTE: The part of the list we care about goes from low to high-1.
    """

    # Pick a random element and move it to the end of the list. This randomness
    # improves performance on partially sorted lists
    p = randrange(low, high)
    if p != high - 1:
        l[p], l[high - 1] = l[high - 1], l[p]
        p = high - 1

    # 'fh' is 'first high'. The index of the first element in the list that's
    # >= the pivot
    fh = low

    # Iterate through the elements in the overall list, creating three
    # sublists as we iterate:
    # (1) The values from i to high-2 are unexamined.
    # (2) The values between low and fh-1 are < the pivot.
    # (3) The values from fh to i+1 are >= the pivot.
    #
    # Note that the pivot itself is at high-1, so we don't need to check it
    for i in xrange(low, high - 1):
        if l[i] < l[p]:
            if fh != i:
                l[i], l[fh] = l[fh], l[i]
            fh += 1

    # At the end of the iteration, the first high element represents the
    # pivot's final location. Since we moved the pivot to the end of the list,
    # we can swap places with the element at fh.
    l[p], l[fh] = l[fh], l[p]

    return fh


def _qsort(l, low, high):
    if high - low > 1:
        p = _partition(l, low, high)
        _qsort(l, low, p)
        _qsort(l, p + 1, high)


def qsort(l):
    """In-place quick sort of a Python list."""
    _qsort(l, 0, len(l))


if __name__ == '__main__':
    from pprint import pprint
    val = [5, 4, 3, 2, 2]
    qsort(val)
    pprint(val)
    assert(val == [2, 2, 3, 4, 5])

    val = []
    qsort(val)
    pprint(val)
    assert(val == [])

    val = [1]
    qsort(val)
    pprint(val)
    assert(val == [1])

    val = [1, 2, 3, 4, 5]
    qsort(val)
    pprint(val)
    assert(val == [1, 2, 3, 4, 5])

    val = [3, 2, 1, 6, 2]
    qsort(val)
    pprint(val)
    assert(val == [1, 2, 2, 3, 6])