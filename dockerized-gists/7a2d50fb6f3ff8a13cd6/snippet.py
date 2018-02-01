#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import sys
import math
import struct

if sys.version_info > (3, 0):
    basestring_type = str
else:
    basestring_type = basestring

HASH_BITS = 61 if struct.calcsize('P') >= 8 else 31
HASH_MODULUS = 2 ** HASH_BITS - 1
PyLong_SHIFT = 30
PyLong_BASE = 1 << PyLong_SHIFT
PyLong_MASK = PyLong_BASE - 1

def toint32(x):
    return int((x & 0xffffffff) - ((x & 0x80000000) << 1))

def toint64(x):
    return int((x & 0xffffffffffffffff) - ((x & 0x8000000000000000) << 1))

def handle_overflow(value):
    """ simulate integer overflow """
    if struct.calcsize('P') * 8 == 64:
        return toint64(value)
    return toint32(value)

def string_hash(str_value):
    if not str_value:
        return 0
    c = str_value[0]
    res = ord(c) << 7
    for c in str_value:
        res = (1000003 * res) ^ ord(c)
    res ^= len(str_value)
    res = handle_overflow(res)
    if res == -1:
        res = -2
    return res

def string_hash_py34(str_value):
    if not str_value:
        return 0
    raise Exception('Unknown SipHash random seed!')

def int_hash(int_value):
    res = handle_overflow(int_value % (2 ** (struct.calcsize('l') * 8) - 1))
    if int_value < 0:
        res = handle_overflow(int_value % (2 ** (struct.calcsize('l') * 8) - 1) + 1)
    if res == -1:
        res = -2
    return res

def get_pylong_from_long(value):
    """
    Get a python long object. Returns a tuple with object size and digits.
    Object size is based on a sign of value and digits number.
    """
    negative = value < 0
    abs_value = abs(value)
    # count the number of digits
    digits = []
    t = abs_value
    while t:
        digits.append(t & PyLong_MASK)
        t >>= PyLong_SHIFT
    long_object_size = -len(digits) if negative else len(digits)
    return long_object_size, digits

def int_hash_py3(int_value):
    digits_num, digits = get_pylong_from_long(int_value)
    if digits_num == -1:
        return -2 if digits[0] == 1 else -digits[0]
    elif digits_num == 0:
        return 0
    elif digits_num == 1:
        return digits[0]
    sign = 1 if int_value > 0 else -1
    # compute a hash
    x = 0
    for d in digits[::-1]:
        x = ((x << PyLong_SHIFT) & HASH_MODULUS) | (x >> (HASH_BITS - PyLong_SHIFT))
        x += d
        if x >= HASH_MODULUS:
            x -= HASH_MODULUS
    x *= sign  # apply sign
    x = handle_overflow(x)
    if x == -1:
        x = -2
    return x

def float_hash_py3(float_value):
    if math.isnan(float_value) or math.isinf(float_value):
        if math.isinf(float_value):
            return -314159 if float_value < 0 else 314159
        else:
            return 0
    m, e = math.frexp(float_value)
    sign = 1
    if m < 0:
        sign = -1
        m = -m
    x = 0
    while m:
        x = ((x << 28) & HASH_MODULUS) | x >> (HASH_BITS - 28)
        m *= 268435456.0  # 2**28
        e -= 28
        y = int(m)  # pull out integer part
        m -= y
        x += y
        if x >= HASH_MODULUS:
            x -= HASH_MODULUS
    # adjust for the exponent; first reduce it modulo HASH_BITS
    e = e % HASH_BITS if e >= 0 else HASH_BITS - 1 - ((-1 - e) % HASH_BITS)
    x = ((int(x) << e) & HASH_MODULUS) | int(x) >> (HASH_BITS - e)
    x *= sign
    x = handle_overflow(x)
    if x == -1:
        x = -2
    return x

def float_hash(float_value):
    if math.isnan(float_value) or math.isinf(float_value):
        if math.isinf(float_value):
            return -271828 if float_value < 0 else 314159
        else:
            return 0
    fractpart, intpart = math.modf(float_value)
    if fractpart == 0.0:
        # this must return the same hash as an equal int or long
        return int_hash(int(float_value))  # use int hash
    fractpart, expo = math.frexp(float_value)
    val = fractpart * 2147483648.0  # 2**31
    hipart = int(val)
    val = (val - float(hipart)) * 2147483648.0  # get the next 32 bits
    res = hipart + int(val) + (expo << 15)
    res = handle_overflow(res)
    if res == -1:
        res = -2
    return res

def complex_hash(complex_value):
    hashreal = float_hash(complex_value.real)
    if hashreal == -1:
        return -1
    hashimag = float_hash(complex_value.imag)
    if hashimag == -1:
        return -1
    res = hashreal + 1000003 * hashimag
    res = handle_overflow(res)
    if res == -1:
        res = -2
    return res

# bool hash is based on int hash
bool_hash = int_hash

def object_hash(object_value):
    res = id(object_value)
    sizeof_void_p = struct.calcsize('P')
    res = handle_overflow((res >> 4) | (res << (8 * sizeof_void_p - 4)))
    if res == -1:
        res = -2
    return res

def tuple_hash(tuple_value):
    mult = 1000003
    res = 0x345678
    tuple_len = len(tuple_value)
    for item in tuple_value:
        tuple_len -= 1
        if isinstance(item, basestring_type):
            item_hash = string_hash(item)
        elif isinstance(item, bool):
            item_hash = bool_hash(item)
        elif isinstance(item, int):
            item_hash = int_hash(item)
        elif isinstance(item, float):
            item_hash = float_hash(item)
        elif isinstance(item, complex):
            item_hash = complex_hash(item)
        elif isinstance(item, tuple):
            item_hash = tuple_hash(item)
        elif isinstance(item, frozenset):
            item_hash = frozenset_hash(item)
        elif isinstance(item, object):
            item_hash = object_hash(item)
        else:
            raise TypeError('unhashable type: %s' % str(type(item))[6:-1])
        if item_hash == -1:
            return -1
        res = (res ^ item_hash) * mult
        mult += int(82520 + tuple_len * 2)
    res += 97531
    res = handle_overflow(res)
    if res == -1:
        res = -2
    return res

def frozenset_hash(frozenset_value):
    h = 1927868237
    h *= len(frozenset_value) + 1
    for item in frozenset_value:
        if isinstance(item, basestring_type):
            item_hash = string_hash(item)
        elif isinstance(item, bool):
            item_hash = bool_hash(item)
        elif isinstance(item, int):
            item_hash = int_hash(item)
        elif isinstance(item, float):
            item_hash = float_hash(item)
        elif isinstance(item, complex):
            item_hash = complex_hash(item)
        elif isinstance(item, tuple):
            item_hash = tuple_hash(item)
        elif isinstance(item, frozenset):
            item_hash = frozenset_hash(item)
        elif isinstance(item, object):
            item_hash = object_hash(item)
        else:
            raise TypeError('unhashable type: %s' % str(type(item))[6:-1])
        h ^= (item_hash ^ (item_hash << 16) ^ 89869747) * 3644798167
    h = h * 69069 + 907133923
    if h == -1:
        h = 590923713
    res = handle_overflow(h)
    return res

# update some functions for python 3
if sys.version_info > (3, 0):
    int_hash = int_hash_py3
    float_hash = float_hash_py3
    if sys.version_info >= (3, 4):
        string_hash = string_hash_py34

def main():
    print('====================================================')
    print('Testing Python hash algorithms')
    print('====================================================')

    print('hash(integer):')
    i = -1234567890123456798
    print(hash(i))
    print(int_hash(i))

    print('---------------')
    print('hash(float):')
    f = 123456789.01234
    print(hash(f))
    print(float_hash(f))

    print('---------------')
    print('hash(complex):')
    c = 1 + 2.34j
    print(hash(c))
    print(complex_hash(c))

    print('---------------')
    print('hash(boolean):')
    b = True
    print(hash(b))
    print(bool_hash(b))

    print('---------------')
    print('hash(None):')
    n = None  # object, type
    print(hash(n))
    print(object_hash(n))

    print('---------------')
    print('hash(object):')
    class A(object): pass
    print(hash(A))
    print(object_hash(A))

    if sys.version_info < (3, 4):
        print('---------------')
        print('hash(string):')
        s = 'Hello world!!!'
        print(hash(s))
        print(string_hash(s))

        print('---------------')
        print('hash(tuple)')
        t = (False, '1', 2, (4.5, 6 - 7.8j, (('deeper',), 'inner')), None, object, type, frozenset([1, 2, 3]))
        print(hash(t))
        print(tuple_hash(t))

        print('---------------')
        print('hash(frozenset)')
        fs = frozenset([30, True, None, '123', 2.3, frozenset({1, '2', frozenset({1, '2', 3})})])
        print(hash(fs))
        print(frozenset_hash(fs))

    print('====================================================')

if __name__ == '__main__':
    main()