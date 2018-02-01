# -*- coding: utf-8 -*-

import hashlib
import sys
import time

# Using: ./hash.py hashcode
# For example: ./hash.py 9743a66f914cc249efca164485a19c5c

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s Time: %0.3f s' % (f.func_name, float(time2 - time1))
        return ret

    return wrap


@timing
def decryptMD5(testHash):
    s = []

    while True:
        m = hashlib.md5()

        for c in s:
            m.update(chr(c))

        hash = m.hexdigest()

        if hash == testHash:
            return ''.join([chr(c) for c in s])

        wrapped = True

        for i in range(0, len(s)):
            s[i] = (s[i] + 1) % 256

            if s[i] != 0:
                wrapped = False
                break

        if wrapped:
            s.append(0)

print(decryptMD5(sys.argv[1]))