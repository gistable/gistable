"""
Python implementation of PKCS #7 padding.

RFC 2315: PKCS#7 page 21
Some content-encryption algorithms assume the
input length is a multiple of k octets, where k > 1, and
let the application define a method for handling inputs
whose lengths are not a multiple of k octets. For such
algorithms, the method shall be to pad the input at the
trailing end with k - (l mod k) octets all having value k -
(l mod k), where l is the length of the input. In other
words, the input is padded at the trailing end with one of
the following strings:

         01 -- if l mod k = k-1
        02 02 -- if l mod k = k-2
                    .
                    .
                    .
      k k ... k k -- if l mod k = 0

The padding can be removed unambiguously since all input is
padded and no padding string is a suffix of another. This
padding method is well-defined if and only if k < 256;
methods for larger k are an open issue for further study.

"""

# Original Source: http://japrogbits.blogspot.com/2011/02/using-encrypted-data-between-python-and.html

# Updated to Python 3.
#   Despite some complaints of Python 3, using it correctly simplified the
#   original greatly.


## @param bytestring    The padded bytestring for which the padding is to be removed.
## @param k             The padding block size.
# @exception ValueError Raised when the input padding is missing or corrupt.
# @return bytestring    Original unpadded bytestring.
def decode(bytestring, k=16):
    """
    Remove the PKCS#7 padding from a text bytestring.

    """

    val = bytestring[-1]
    if val > k:
        raise ValueError('Input is not padded or padding is corrupt')
    l = len(bytestring) - val
    return bytestring[:l]


## @param bytestring    The text to encode.
## @param k             The padding block size.
# @return bytestring    The padded bytestring.
def encode(bytestring, k=16):
    """
    Pad an input bytestring according to PKCS#7
    
    """
    l = len(bytestring)
    val = k - (l % k)
    return bytestring + bytearray([val] * val)


# Tests
# =====
import unittest

class Pkcs7Test(unittest.TestCase):
    def test_pkcs7(self):
        # Not a unit at all, but whatever.
        import pkcs7
        import os
        import random

        def test(text):
            a = pkcs7.encode(text)
            b = pkcs7.encode(text)
            assert len(a) % 4 == 0
            assert len(b) % 4 == 0
            assert a == b

        for i in range(1000):
            text = os.urandom( int(random.random()*10000) )
            test(text)