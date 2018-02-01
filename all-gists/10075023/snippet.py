#!/usr/bin/env python
#-*- coding: utf-8 -*-

def left_shift(n):
    return n + n

def is_bit_on(n, bit):
    a = n % bit
    b = n % left_shift(bit)
    if not b:
        return False
    if b - a == 0:
        return False
    return True

def right_shift(n):
    a = 1
    b = 2
    retval = 0
    while n > a:
        if is_bit_on(n, b):
            retval += a
        a = left_shift(a)
        b = left_shift(b)
    return retval

if __name__ == '__main__':
    for x in range(255):
	assert (x << 1) == left_shift(x), "left shift : {}, {}".format(x << 1, left_shift(x))
        assert (x >> 1) == right_shift(x), "right shift : {}, {}".format(x >> 1, right_shift(x))