#!/usr/bin/env python
from z3 import *


def display_model(m):
    block = {}
    for x in m:
        if 'b' in str(x):
            block[ord(str(x)[-1:])] = int(str(m[x]))

    password = ''.join(map(chr, block.values()))
    print password


def get_models(F):
    s = Solver()
    s.add(F)
    while True:
        if s.check() == sat:
            m = s.model()
            display_model(m)
            block = []
            for d in m:
                if d.arity() > 0:
                    raise Z3Exception("uninterpreted functions are not suppported")
                c = d()
                if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                    raise Z3Exception("arrays and uninterpreted sorts are not supported")
                block.append(c != m[d])
            s.add(Or(block))
        else:
            break


def is_alphanum(x):
    return Or(And(x >= 0x41, x <= 0x5a), And(x >= 0x61, x <= 0x7a), And(x >= 0x30, x <= 0x39))


def calculate(password):
    ret = BitVec('ret', 32)
    i = BitVec('i', 8)
    ret = 0

    for i in range(len(password)):
        ret = If(password[i] & 0x01 > 0, ret + 1, ret)
        ret = If(password[i] & 0x02 > 0, ret + 3, ret)
        ret = If(password[i] & 0x04 > 0, ret + 128, ret)
        ret = If(password[i] & 0x08 > 0, ret + 64, ret)
        ret = If(password[i] & 0x10 > 0, ret + -3, ret)
        ret = If(password[i] & 0x20 > 0, ret + -1, ret)
        ret = If(password[i] & 0x40 > 0, ret * 64, ret)

    return ret

if __name__ == '__main__':
    for length in range(100):
        print '[+] Trying with length %d ...' % length
        F = []
        password = [BitVec("b%d" % i, 8) for i in range(length)]

        F.extend([is_alphanum(password[i]) for i in range(length)])
        F.extend([
            calculate(password) == 4919
        ])

        get_models(F)
