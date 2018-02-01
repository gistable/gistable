#!/usr/bin/env python3.4

"""Smallest number evenly divisible by all of the numbers from 1 to 20?

http://projecteuler.net/problem=5

"""

import collections
import itertools


def prime_factorization(n: int) -> "set of ints":
    prime_numbers = []

    prime = 2
    while n > 1:
        if n % prime:
            if prime == 2:
                prime += 1
            else:
                prime += 2
            continue
        prime_numbers.append(prime)
        n //= prime

    prime_repeats_set = set()
    for prime in prime_numbers:
        prime_repeats_set.add((prime, prime_numbers.count(prime)))

    return prime_repeats_set


def main():
    max_no = 20

    prime_repeats_set = set()
    for n in range(1, max_no + 1):
        prime_repeats_set.update(prime_factorization(n))


    factors = collections.defaultdict(list)
    for prime, repeats in prime_repeats_set:
        factors[prime].append(repeats)

    minimum_number = 1
    for prime, repeats_list in factors.items():
        minimum_number *= prime ** max(repeats_list)

    print(minimum_number)


if __name__ == "__main__":
    main()