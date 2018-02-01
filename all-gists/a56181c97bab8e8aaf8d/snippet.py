#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    $ time python balance.py
    1133135930 ['L', 'R', 'R', 'R', 'L', 'R', 'R', 'L', 'R', 'L', 'L', 'R', 'L', '-', '-', 'R', 'L', '-', '-', 'R']
    python balance.py  0.02s user 0.01s system 91% cpu 0.032 total
"""

def inc_one_digit(n):
    if n == 'L':
        return False, '-'
    elif n == '-':
        return False, 'R'
    elif n == 'R':
        return True, 'L'

def dec_one_digit(n):
    if n == 'L':
        return True, 'R'
    elif n == '-':
        return False, 'L'
    elif n == 'R':
        return False, '-'

def number(A):
    s = ['-'] # 0
    for _ in xrange(A):
        s = increase(s)
    return s

def evaluate(A):
    s = 0
    for i, x in enumerate(A):
        s += 3**i * ({'L': -1, '-': 0, 'R': 1}[x])
    return s

def increase(A):
    B = []
    c = True
    for x in A:
        if c:
            c, x = inc_one_digit(x)
        B.append(x)
    if c:
        B.append('R')
    return B

def add_one_digit(A, B):
    if A == 'L' and B == 'L':
        return -1, 'R'
    elif A == 'L' and B == '-':
        return 0, 'L'
    elif A == 'L' and B == 'R':
        return 0, '-'
    elif A == '-' and B == 'L':
        return 0, 'L'
    elif A == '-' and B == '-':
        return 0, '-'
    elif A == '-' and B == 'R':
        return 0, 'R'
    elif A == 'R' and B == 'L':
        return 0, '-'
    elif A == 'R' and B == '-':
        return 0, 'R'
    elif A == 'R' and B == 'R':
        return 1, 'L'

def trim(A):
    for i in range(len(A)):
        if A[len(A)-i-1] != '-':
            return A[:len(A)-i]
    return A

def add(A, B):
    l = max(len(A), len(B)) + 1
    A = list(A) + (['-' for _ in xrange(l-len(A))])
    B = list(B) + (['-' for _ in xrange(l-len(B))])
    C = ['-' for _ in xrange(l)]
    c = 0
    for x in xrange(l):
        c, v = add_one_digit(A[x], B[x])
        cc, v = add_one_digit(v, C[x])
        c += cc
        C[x] = v
        if c < 0:
            while c < 0:
                x += 1
                cc, v = dec_one_digit(C[x])
                c += 1
                C[x] = v
                if cc: c -= 1
        elif c > 0:
            while c > 0:
                x += 1
                cc, v = inc_one_digit(C[x])
                c -= 1
                C[x] = v
                if cc: c += 1
    return trim(C)

def ten_to_the_nth(x):
    A = number(1)
    B = ['-']
    for _ in xrange(x):
        for _ in xrange(10):
            B = add(A, B)
        A = B
        B = ['-']
    return A

def answer(x):
    n = 0
    S = ['-']
    while x:
        A = x % 10
        ten = ten_to_the_nth(n)
        for _ in xrange(A):
            S = add(S, ten)
        x -= A
        x = x / 10
        n += 1
    return S

A = answer(1133135930)
print evaluate(A), A