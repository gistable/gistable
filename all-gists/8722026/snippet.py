#! /usr/bin/env python3
from functools import lru_cache
from itertools import count, takewhile

numbers = count(1)

MAX = 4000000

@lru_cache(maxsize=None)
def fib(n) :
    if n < 3 :
        return 1
    else :
        return fib(n-2) + fib(n-1)


fibs = (fib(x) for x in numbers)
even_fibs = (x for x in fibs if x % 2 == 0)

even_fibs_under_max = takewhile(lambda x : x < MAX, even_fibs)

print(sum(x for x in even_fibs_under_max))