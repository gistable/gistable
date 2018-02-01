"""
The shellcode in Challege 6 compares the string in RDI
against a bunch of conditions. This script extracts the
conditions and solves the constraints, yielding the
expected string.
"""
from idaapi import *
from williutils import *


def ror(x, n, bits = 32):
    mask = (2L**n) - 1
    mask_bits = x & mask
    return (x >> (n % bits) | (mask_bits << ((bits - n) % bits)))


def rol(x, n, bits = 32):
    return ror(x, (bits - n) % bits, bits=bits)


def mask(c):
    return c & 0xFF


# these functions do the inverse of their lowercase counterpart
# so by applying them in reverse, then we can solve the simple constraint

def ADD(c, x):
    return mask(c - x)


def SUB(c, x):
    return mask(c + x)


def XOR(c, x):
    return mask(c ^ x)


def ROL(c, x):
    return mask(ror(c, x, 8))


def ROR(c, x):
    return mask(rol(c, x, 8))


def get_handler(mnem):
    return {
            "add": ADD,
            "sub": SUB,
            "xor": XOR,
            "ror": ROR,
            "rol": ROL}[mnem]



START = 0x1C


def solve_one_character(ea):
    c = GetOperandValue(ea, 1)
    print "START", hex(c)
    ea = PrevHead(ea)

    while "[rax]" in GetOpnd(ea, 0):
        print(GetMnem(ea).upper(), hex(GetOperandValue(ea, 1)))
        c = get_handler(GetMnem(ea))(c, GetOperandValue(ea, 1))
        ea = PrevHead(ea)
    print "solved: " + chr(c)
    return c


def main():
    ret = ""
    ea = scan_forwards(START, mnem="cmp")
    while ea:
        ret += chr(solve_one_character(ea))
        try:
            ea = scan_forwards(ea, mnem="cmp")
        except RuntimeError:
            print(ret)
            return



if __name__ == "__main__":
    main()
