#!/usr/bin/env python2
# Functional Python: reduce, map, filter, lambda, *unpacking


# REDUCE EXAMPLE
add = lambda *nums: reduce(lambda x, y: x + y, nums)

def also_add(*nums):
    '''Does the same thing as the lambda expression above.'''
    def add_two_numbers(x, y):
        return x + y
    return reduce(add_two_numbers, nums)

print add(1, 2, 3) # 6
print add(*range(10)) # sum of 0-9: 45


# MAP EXAMPLE
squares = lambda *nums: map(lambda x: x * x, nums)

def also_squares(*nums):
    '''Does the same thing as the lambda expression above.'''
    def double(x):
        return x * x
    return map(double, nums)

print squares(1, 2, 3) # [1, 4, 9]
print squares(*range(10)) # list of squares 0-9
print add(*squares(*range(10))) # sum of the above squares: 285


# FILTER EXAMPLE
evens = lambda *nums: filter(lambda x: x % 2 == 0, nums)

def also_evens(*nums):
    '''Does the same thing as the lambda expression above.'''
    def is_even(x):
        return x % 2 == 0
    return filter(is_even, nums)

print evens(1, 2, 3) # (2,)
print evens(1, 3) # ()
print evens(*range(10)) # (0, 2, 4, 6, 8)
