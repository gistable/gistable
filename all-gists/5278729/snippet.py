#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Test that I passed on codility.com for TopTal company
#


# Task #1
def binary_gap(N):
    '''
    A binary gap within a positive integer N is any maximal
    sequence of consecutive zeros that is surrounded by ones
    at both ends in the binary representation of N.

    Args:
      - N: integer within the range [1..2,147,483,647]
    '''
    bin_representation = bin(N)[2:]
    max_gap = 0
    gap_counter = 0
    gap_started = False
    for symbol in bin_representation:
        if symbol == '1':
            if gap_counter > max_gap:
                max_gap = gap_counter
            gap_counter = 0
            gap_started = True
        elif gap_started:
            gap_counter += 1
    return max_gap

print binary_gap(1041)



# Task #2
def count_div(A, B, K):
    '''
    Returns the number of integers within the range [A..B] that are divisible by K.

    Used generators to save memory on large amounts of data.

    Args:
      - A: is an integer within the range [0..2,000,000,000]
      - B: is an integer within the range [0..2,000,000,000] and A <= B
      - K: is an integer within the range [1..2,000,000,000]
    '''
    divs_count = 0
    for x in xrange(A, B + 1):
        if (x % K) == 0:
            divs_count += 1
    return divs_count

print count_div(1, 200000000, 1000)



# Task #3
def triangle(A):
    '''
    Calculate triangel of integers, where sentense of numbers P, Q, R
    correspond to next rules:
     - P + Q > R
     - Q + R > P
     - R + P > Q

    Args:
      - A: list of integers, where we will search triangle

    Return: 1 - if triangle exists, and 0 - otherwise
    '''
    A = tuple(enumerate(A))
    for p, P in A:
        for q, Q in A[p + 1:]:
            for r, R in A[q + 1:]:
                if (P + Q > R) and (Q + R > P) and (R + P > Q):
                    return 1 
    return 0

print triangle([10, 2, 5, 1, 8, 20])