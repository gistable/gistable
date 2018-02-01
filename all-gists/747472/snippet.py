#!/usr/bin/env python
from struct import pack, unpack

def vb_encode(number):
    bytes = []
    while True:
        bytes.insert(0, number % 128)
        if number < 128:
            break
        number /= 128
    bytes[-1] += 128
    return pack('%dB' % len(bytes), *bytes)

def vb_decode(bytestream):
    n = 0
    numbers = []
    bytestream = unpack('%dB' % len(bytestream), bytestream)
    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            numbers.append(n)
            n = 0
    return numbers

# test
if __name__ == '__main__':
    # format() require python 2.6 or more.
    def test_vb_encode(number, ok):
        bytestream = vb_encode(number)
        assert ''.join([format(b, '08b') for b in unpack('%dB' % len(bytestream), bytestream)]) == ok
        print "test ok. %s -> %s" % (number, ok)
    
    test_vb_encode(1,   '10000001')
    test_vb_encode(5,   '10000101')
    test_vb_encode(127, '11111111')
    test_vb_encode(128, '00000001' + '10000000')
    test_vb_encode(129, '00000001' + '10000001')
    
    import sys, random
    for i in xrange(1000):
        n = random.randint(0, sys.maxint)
        assert vb_decode(vb_encode(n))[0] == n
