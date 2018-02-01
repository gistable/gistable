#!/usr/bin/env python3
# Peter Simonyi  1 June 2012
'''A binary clock: prints the current time (HHMMSS) in binary-coded decimal.

Each BCD digit takes one column; least-significant bits are at the bottom.
Example: at 21:14:59 (local time):
000001
000110
100000
011011
'''

import time
from itertools import zip_longest


def main():
    print(vertical_strings(bcd(time.strftime('%H%M%S'))))

# bcd :: iterable(characters '0'-'9') -> [str]
def bcd(digits):
    'Convert a string of decimal digits to binary-coded-decimal.'
    def bcdigit(d):
        'Convert a decimal digit to BCD (4 bits wide).'
        # [2:] strips the '0b' prefix added by bin(). 
        return bin(d)[2:].rjust(4, '0')
    return (bcdigit(int(d)) for d in digits)

# vertical_strings :: iterable(str) -> str
def vertical_strings(strings):
    'Orient an iterable of strings vertically: one string per column.'
    iters = [iter(s) for s in strings]
    concat = ''.join
    return '\n'.join(map(concat,
                         zip_longest(*iters, fillvalue=' ')))


if __name__ == '__main__':
    main()

