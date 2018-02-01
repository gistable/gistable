#!/usr/bin/env python
# Quick Sort Implementation in Python
# Author: Arunprasath Shankar
# Case Western Reserve University

# Using Partition Method

from random import randint


def quickSort(lst):
    if not lst:
        return []
    else:
        pivot_index = randint(0, len(lst) - 1)
        pivot = lst[pivot_index]
        lesser = quickSort([l for i, l in enumerate(lst)
                            if l <= pivot and i != pivot_index])
        greater = quickSort([l for l in lst if l > pivot])
        #print lesser, pivot, greater
        return lesser + [pivot] + greater


print quickSort([3, 2, 5, 6, 1, 7, 2, 4, 234, 234, 23, 1234, 24, 132])