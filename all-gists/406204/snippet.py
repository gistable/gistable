#!/usr/bin/python
#
# See http://stackoverflow.com/questions/1016997/generate-from-generators
#
# Equivalent implementation in Python of this Haskell code:
#    
# grandKids generation kidsFunc val =
#     iterate (concatMap kidsFunc) [val] !! generation

from itertools import chain, islice, imap
from functools import partial

# Generic functions

def flatten(it):
    "Flatten one level of nesting"
    return chain.from_iterable(it)

def concatMap(func, it):
    """Map a function over a list and concatenate the results."""
    return flatten(imap(func, it))

def iterate(func, x):
    """Yield repeated applications of f to x: x, f(x), f(f(x)), ..."""    
    while 1: 
        yield x
        x = func(x)

def takeN(it, n):
    """Take the n-th element in iterator."""
    return islice(it, n, None).next()

###

def kids(x): # children indices in a 1-based binary heap
    yield x*2
    yield x*2 + 1

def grandKids(generation, kidsFunc, val):
    return takeN(iterate(partial(concatMap, kidsFunc), [val]), generation)

print list(grandKids(3, kids, 2))
# [16, 17, 18, 19, 20, 21, 22, 23]
