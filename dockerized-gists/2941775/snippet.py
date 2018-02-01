#! /usr/bin/python
# coding: UTF-8

import sys

def main():
    a = []
    for line in sys.stdin:
        a.append(int(line))
    print count_inversions(a, 0, len(a) - 1)

def count_inversions(a, p, r):
    inversions = 0
    if p < r:
        q = (p + r) / 2
        inversions += count_inversions(a, p, q)
        inversions += count_inversions(a, q+1, r)
        inversions += merge_inversions(a, p, q, r)
    return inversions

INFINITY = 99999999

def merge_inversions(a, p, q, r):
    n1 = q - p + 1
    n2 = r - q
    L = []
    R = []
    for i in range(n1):
        L.append(a[p+i])
    for j in range(n2):
        R.append(a[q+j+1])
    L.append(INFINITY)
    R.append(INFINITY)
    i = 0
    j = 0
    inversions = 0
    counted = False
    for k in range(p, r+1):
        if not counted and R[j] < L[i]:
            inversions += n1 - i
            counted = True
        if L[i] <= R[j]:
            a[k] = L[i]
            i += 1
        else:
            a[k] = R[j]
            j += 1
            counted = False
    return inversions

if __name__ == '__main__':
    main()
