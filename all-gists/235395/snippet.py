#!/usr/bin/env python
"""Measure performance for 3 cases:

1. dict has key at the start of list
2. dict has key at the end of list
3. dict has no key in a list

See http://stackoverflow.com/questions/1737778/dict-has-key-from-list
"""
from functools import wraps
from itertools import imap


def to_compare(function):
    """Decorator to add `function` to global comparison registry.

    NOTE: It changes interface of the `function` in order to use make-figure.py
    """
    if not hasattr(to_compare, 'functions'):
        to_compare.functions = []
    @wraps(function)
    def wrapper(args): # transform interface for make-figure.py
        return function(args[0], args[1])
    to_compare.functions.append(wrapper)
    return wrapper


@to_compare
def mgag_loop(myDict, myList):
    for i in myList:
        if i in myDict:
            return True
    return False

@to_compare
def ronny_any(myDict, myList):
    return any(x in myDict for x in myList)

@to_compare
def ronny_set(myDict, myList):
    return set(myDict) & set(myList)

@to_compare
def pablo_len(myDict, myList):
    return len([x for x in myList if x in myDict]) > 0

@to_compare
def jfs_map(my_dict, my_list):
    return any(map(my_dict.__contains__, my_list))

@to_compare
def jfs_imap(my_dict, my_list):
    return any(imap(my_dict.__contains__, my_list))
    

def args_key_at_start(n):
    'Make args for comparison functions "key at start" case.'
    d, lst = args_no_key(n)
    lst.insert(0, n//2)
    assert (n//2) in d and lst[0] == (n//2)
    return (d, lst)

def args_key_at_end(n):
    'Make args for comparison functions "key at end" case.'
    d, lst = args_no_key(n)
    lst.append(n//2)
    assert (n//2) in d and lst[-1] == (n//2)
    return (d, lst)

def args_no_key(n):
    'Make args for comparison functions "no key" case.'
    d = dict.fromkeys(xrange(n))
    lst = range(n, 2*n+1)
    assert not any(x in d for x in lst)
    return (d, lst)
    

if __name__ == '__main__':
    from subprocess import check_call
    import sys

    # check that all function produce expected result
    assert all(f(make_args(5))
               for f in to_compare.functions
               for make_args in [args_key_at_start, args_key_at_end])
    assert not any(f(make_args(5))
                   for f in to_compare.functions
                   for make_args in [args_no_key])

    # measure performance and plot it
    check_call(
        ["python", "make-figures.py"] +
        ["--sort-function=main." + f.__name__ for f in to_compare.functions] +
        ["--sequence-creator=main." + f.__name__
         for f in (args_key_at_start, args_key_at_end, args_no_key)] +
        sys.argv[1:])
