#!/usr/bin/env python
"""(c) gorlum0 [at] gmail.com"""
import random
from sys import maxsize as inf

def merge_sort(A):
    """merge-sort which counts inversions"""
    def merge(L, R):
        m = len(L)-1
        B = []
        i = j = 0
        inv = 0
        while L[i] != inf or R[j] != inf:
            if L[i] <= R[j]:
                B.append(L[i])
                i += 1
            else:
                B.append(R[j])
                inv += m - i
                j += 1
        return B, inv

    n = len(A)
    inv = 0
    if n >= 2:
        mid = n // 2
        L, R = A[:mid], A[mid:]
        L, inv_left = merge_sort(L)
        R, inv_right = merge_sort(R)
        A, inv_split = merge(L + [inf], R + [inf])
        inv = inv_left + inv_right + inv_split
    return A, inv
            

if __name__ == '__main__':
    A = [randint(0, 100) for _ in xrange(5)]
    
    print A
    A, inv = merge_sort(A)
    print inv
    print A
