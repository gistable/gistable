#!/usr/bin/env python
# http://stackoverflow.com/questions/5480131/will-python-systemrandom-os-urandom-always-have-enough-entropy-for-good-crypto
import math
import random
import sys

CHOICES = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$^&*()+/?,.'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: %s password-length'
        sys.exit(1)
    pw_len = int(sys.argv[1])

    pw = ''
    for _ in xrange(pw_len):
        pw += random.SystemRandom().choice(CHOICES)

    print pw
    print 'total bits of entropy: %s' % (math.log(len(CHOICES), 2) * pw_len)