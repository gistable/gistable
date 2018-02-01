#!/usr/bin/env python
# -*-coding: utf-8 -*-

### Written by Amit
# Algorithm: Binary GCD
# Work Flow:
# 1. gcd(0, v) = v, because everything divides zero, and v is the largest number
# that divides v. Similarly, gcd(u, 0) = u. gcd(0, 0) is not typically defined,
# but it is convenient to set gcd(0, 0) = 0.
# 2. If u and v are both even, then gcd(u, v) = 2·gcd(u/2, v/2),
# because 2 is a common divisor. # 3. If u is even and v is odd,
# then gcd(u, v) = gcd(u/2, v), because 2 is not a common divisor.
# Similarly, if u is odd and v is even, then gcd(u, v) = gcd(u, v/2).
# 4. If u and v are both odd, and u ≥ v, then gcd(u, v) = gcd((u − v)/2, v).
# If both are odd and u < v, then gcd(u, v) = gcd((v − u)/2, u).
# These are combinations of one step of the simple Euclidean algorithm,
# which uses subtraction at each step, and an application of step 3 above.
# The division by 2 results in an integer because the difference of two odd
# numbers is even.[3]
# 5. Repeat steps 2–4 until u = v, or (one more step) until u = 0.
# In either case, the GCD is 2kv, where k is the number of common factors of 2
# found in step 2.

k = 0
result = 1

def condition_one(u, v):
    '''
    checks if either u or v is zero,
    gcd(0, v) = v, because everything divides zero, and v is the largest number
    that divides v. Similarly, gcd(u, 0) = u. gcd(0, 0) is not typically defined,
    but it is convenient to set gcd(0, 0) = 0.
    returns false if u != 0 and v != 0
    '''
    print 'condition one', u, v
    if u == 0 or v == 0:
        if u == v:
            return 0
        if u == 0:
            return v
        else:
            return u
    else:
        return False

def condition_zero(u, v):
    '''
    Returns True if u == v
    '''
    print 'condition zero', u, v
    if u == v:
        return True
    else:
        return False

def condition_two(u, v):
    global k
    '''
    If u and v are both even, then gcd(u, v) = 2·gcd(u/2, v/2), because 2 is a
    common divisor.
    returns True if u and v are both divisible by 2.
    Otherwise, returns False
    '''
    print 'condition two', u, v
    if u % 2 == 0 and v % 2 == 0:
        k += 1
        return True
    else:
        return False

def condition_three(u, v):
    '''
    If u is even and v is odd, then gcd(u, v) = gcd(u/2, v),
    because 2 is not a common divisor.
    Similarly, if u is odd and v is even, then gcd(u, v) = gcd(u, v/2).
    '''
    print 'condition three', u, v
    if u % 2 == 0:
        return 1
    elif v % 2 == 0:
        return 2
    else:
        return False
    
def condition_four(u, v):
    '''
    4. If u and v are both odd, and u ≥ v, then gcd(u, v) = gcd((u − v)/2, v).
    If both are odd and u < v, then gcd(u, v) = gcd((v − u)/2, u).
    These are combinations of one step of the simple Euclidean algorithm,
    which uses subtraction at each step, and an application of step 3 above.
    The division by 2 results in an integer because the difference of two odd
    numbers is even.[3]
    '''
    print 'condition four', u, v 
    if condition_three(u, v) == False:
        if u >= v:
            return 1
        else:
            return 2

def __calculate_gcd(u, v):
    global result
    ''' find gcd of numbers1 and number2
    u - numer one
    v - number two
    '''
    if condition_zero(u, v) == True:
        result = u
        return
    if condition_one(u, v) != False:
        result = condition_one(u, v)
        return
    if condition_two(u, v) == True:
        find_gcd(u/2, v/2)
    elif condition_three(u, v) == 1:
        find_gcd(u/2, v)
    elif condition_three(u, v) == 2:
        find_gcd(u, v/2)
    else:
        if condition_four(u, v) == 1:
            find_gcd((u - v ) / 2, v)
        elif condition_four (u, v) == 2:
            find_gcd((v - u)/2, u)

def find_gcd(u, v):
    '''
    calculates gcd
    u - first number
    v - second number
    '''
    __calculate_gcd(u, v)
    if k == 0:
        return result
    else:
        return (2 * k * result)
        
print find_gcd(8, 4)