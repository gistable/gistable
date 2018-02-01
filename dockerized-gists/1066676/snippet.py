# -*- coding: utf-8 -*-

import math

def is_prime(n):
    for i in xrange(2, int(math.sqrt(n)) + 1):
        if not n % i:
            return False
    return True

def main():
    return [i for i in xrange(2, 101) if is_prime(i)]

if __name__ == '__main__':
    print main()
