#!/usr/bin/env python

def equi(A):
    upper = sum(A)
    lower = 0
    for position in range(0, len(A)):
        if upper - A[position] == lower:
            return position
        else:
            lower += A[position]
            upper -= A[position]
    return -1

if __name__ == '__main__':
    a = [-7, 1, 5, 2, -4, 3, 0]
    print equi(a)