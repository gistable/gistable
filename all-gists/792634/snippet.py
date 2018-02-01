'''
Implementation of Poly1305-AES as described by Daniel J. Bernstein in
documents linked from: http://cr.yp.to/mac.html

Implemented by Josiah Carlson <josiah.carlson@gmail.com> on 2011-01-23,
released into the public domain.

Note: this implementation of Poly1305-AES uses Python's built-in long integer
implementation, so is not terribly performant, and likely suffers from a
side-channel attack related to the timing of bigint modulo. It also uses
PyCrypto's AES encryption implementation, which you will need to have
installed (or update the code with a work-alike).


This source also includes the equivalent of:
  http://cr.yp.to/mac/test-poly1305aes.c
... which can verify the correctness of the included poly1305 implementation
using the hashes provided:
  http://cr.yp.to/mac/test.html


If you want something faster, use SHA256/512 HMAC with a 16/32+ byte secret
key with 16/32+ byte nonce.

'''

import array
from hashlib import md5
import os
import struct
import sys
import time

from Crypto.Cipher import AES

class VerificationFailed(Exception):
    pass

def poly1305(k, r, m, nonce=None, enc_alg=AES):
    '''
    Given a 16-byte secret AES k, an additional 16-byte secret key r, and a
    message m provided as strings, will generate the 16-byte Poly1305-AES
    verifier with a siingle-use 16-byte nonce appended.

    If you wish to provide your own nonce, you can provide it, but be sure
    that you aren't compromising security for the sake of "do it yourself".
    '''
    
    if not nonce:
        nonce = struct.pack('>d', time.time()) + os.urandom(8)

    assert len(k) == 16
    assert len(r) == 16

    r = map(ord, r)
    for index in (3, 7, 11, 15):
        r[index] &= 15
    for index in (4, 8, 12):
        r[index] &= 252
    
    rbar = 0
    for p, v in enumerate(r):
        rbar += v << (8*p)

    h = 0
    s = map(ord, enc_alg.new(k).encrypt(nonce))
    p = (1 << 130) - 5

    lm = len(m)
    for jj in xrange(0, lm, 16):
        c = 0
        for j in xrange(jj, min(jj+16, lm)):
            c += ord(m[j]) << (8*(j-jj))
        c += 1 << (8*(j-jj+1))
        h = ((h + c) * rbar) % p

    for j, sj in enumerate(s):
        h += sj << (8*j)

    out = ''
    for i in xrange(16):
        out += chr(h&255)
        h >>= 8

    return out + str(nonce)

def poly1305_verify(k, r, inp, an=None, enc_alg=AES):
    '''
    Given a 16-byte secret AES k, an additional 16-byte secret key r, and the
    message with a claimed correct verifier+nonce prepended to the message,
    this will verify that the message has not been modified or forged.

    On verification failure, will the VerificationFailed exception. On success
    will return True.

    Why raise an exception and not return false? Message verification failure
    should be an exceptional condition and require explicit handling.
    '''
    if an is None:
        an = inp[:32]
        inp = buffer(inp, 32, len(inp))
    verify = an[:16]
    nonce = an[16:32]
    to_verify = poly1305(k, r, inp, nonce, enc_alg)
    same = not sum(ord(a)^ord(b) for a,b in zip(an, to_verify))
    if not same:
        raise VerificationFailed
    return True

def main():
    '''
    Tests the implementation of poly1305() and poly1305_verify()
    '''
    _buffer = buffer
    _wanted = {
        10010:'ad3314ecd86351da7a20244097a08de6',
        123456:'707212358360ae459bc0ef293a5354e8',
        1234567:'3b2bc877e4e64efbfe39945ac102c768',
        12345678:'ef3831c8b2087ebf6844f2265e1da2c2',
        123456789:'5e29ea7450475dc419a0f95afde0cfdc',
        1001000000:'3ceb64843c00984c5c2b7897f499141b',
        1001000001:None,
    }

    hashed = md5()
    MAXLEN = 1000
    LC = 0
    MAXLC = 2**64
    k = array.array('B', 16*[0])
    r = array.array('B', 16*[0])
    n = array.array('B', 16*[0])
    m = array.array('B', MAXLEN*[0])
    for loop in xrange(1000000):
        l = 0
        while True:
            out = array.array('B', poly1305(_buffer(k), _buffer(r), _buffer(m, 0, l), _buffer(n)))
            h = out.tostring()[:16].encode('hex')
            if '--actually-print' in sys.argv:
                print h
            hashed.update(h + '\n')
            LC += 1
            if LC in _wanted:
                assert hashed.hexdigest() == _wanted[LC], (LC, hashed.hexdigest(), _wanted[LC])
                print >>sys.stderr, time.asctime(), "passed %i lines"%(LC,)
            try:
                poly1305_verify(_buffer(k), _buffer(r), _buffer(m, 0, l), _buffer(out))
            except VerificationFailed:
                print "poly1305_verify failed"
                sys.exit(1)

            x = ord(os.urandom(1)) & 15
            y = 1 + (ord(os.urandom(1))%255)
            out[x] ^= y
            try:
                poly1305_verify(_buffer(k), _buffer(r), _buffer(m, 0, l), _buffer(out))
            except VerificationFailed:
                pass
            else:
                print "poly1305_verify succeeded on bad input"
                sys.exit(1)

            out[x] ^= y
            if l >= MAXLEN:
                break

            n[0] ^= loop & 255
            for i in xrange(16):
                n[i] ^= out[i]
            if l % 2:
                for i in xrange(16):
                    k[i] ^= out[i]
            if l % 3:
                for i in xrange(16):
                    r[i] ^= out[i]
            m[l] ^= out[0]
            l += 1
            if LC >= MAXLC:
                return

if __name__ == '__main__':
    try:
        # try to make it a bit faster....
        import psyco
        psyco.full()
    except:
        pass
    print >>sys.stderr, '''
Now testing this poly1305 implementation.
Expected runtime to completion on a modern desktop running CPython is around
10 days +/-. If this passes any checkpoint (10010, 123456, etc., lines), then
it is likely not suffering from any debilitating implementation flaw (at least
in terms of correctness, no guarantees regarding sideband attacks), and you
can probably kill it.
'''
    print >>sys.stderr, time.asctime(), "Starting..."
    t = time.time()
    main()
    print >>sys.stderr, time.asctime(), time.time()-t, "seconds elapsed"
