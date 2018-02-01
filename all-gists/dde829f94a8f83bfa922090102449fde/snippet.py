#!/usr/bin/python

# Written by: Michael McKinnon @bigmac
# Get in contact with me if you found this useful

import os
import sys
import gmpy2
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# This Python script is an implementation of the research here: https://eprint.iacr.org/2004/147.pdf
# my eternal thanks to those authors, this helped me solve a CTF challenge whereby I had to recover an
# RSA private key from just two things:
#
# dP - CRT Exponent 1 (i.e. d mod (p-1))
# dQ - CRT Exponent 2 (i.e. d mod (q-1))
#
# Using just these two elements it IS possible to recover the primes p and q - and then to reconstruct
# the entire RSA private key.
#
# Great site here to experiment with RSA keys:
# http://www.mobilefish.com/services/rsa_key_generation/rsa_key_generation.php

def rsa_decrypt(p, q, ciphertext, e=65537):
    '''
    I will take your ciphertext and primes p,q (and optionally e) and decrypt
    using a newly constructed RSA private key. Decrypt with assumed PKCS1_v1_5 padding.

    Call it with something like:
    rsa_decrypt(p, q, open('file.enc').read())

    This probably won't work if your ciphertext is bigger than the total bitlength of (p*q)
    so you'd need to play around with aes-cbc etc.
    '''
    def rsa_keyfromprimes(p, q, e): 
        # we have e from the param - this is the publicExponent
        # calculate n (modulus) is the product of p and q
        n = long(gmpy2.mul(p, q))
        # we need phi(n)
        phi = (p - 1)*(q - 1)
        # calculate d (the privateExponent)
        d = long(gmpy2.invert(e,(p-1)*(q-1)))
        #make the key
        key = RSA.construct((n, long(e), d, p, q))
        # Oh, while we're here have a new private key if you want
        #print key.exportKey()
        return key

    # get the key
    key = rsa_keyfromprimes(p, q, e)
    # get a PKCS cipher object for padding
    cipher = PKCS1_v1_5.new(key)
    # decrypt the ciphertext
    decrypted = cipher.decrypt(ciphertext, None)
    return str(decrypted)

def rsa_recovery(dp, dq, ciphertext, keysize=1024, start=3):
    '''
    This extensive process loops through all unknown e, typically between 3..65537
    and given the dP and dQ will search for primes p and q, then attempt to
    decrypt the ciphertext that is known to have been encrypted with them.
    '''
    # init counters
    r, p, q, d, count, count2, count3 = (0L, 0L, 0L, 0L, 0, 0, 0) 
    # start generalised loop for an unknown e
    for j in range(start, 65538, 2):
        dp1 = long(gmpy2.mul(dp, j) - 1)
        for k in range(3, j):
            d = long(k)
            a, r = gmpy2.t_divmod(dp1, d)
            assert(dp1 == (k * a) + r)
            if r == 0:
                count += 1
                p = long(a + 1)
                if gmpy2.is_odd(p) and gmpy2.is_strong_prp(p, 10):
                    count2 += 1
                    dq1 = long(gmpy2.mul(dq, j) - 1)
                    for l in range(3, j):
                        d = long(l)
                        a, r = gmpy2.t_divmod(dq1, d)
                        assert(dq1 == (l * a) + r)
                        if r == 0:
                            q = long(a + 1)
                            if gmpy2.is_odd(q) and gmpy2.is_strong_prp(q, 10):
                                count3 += 1
                                # just some basic progress on the console
                                if count3 % 10 == 0:
                                    sys.stdout.write('.')
                                    sys.stdout.flush()
                                # only attempt the decrypt if p,q are expected bitlength
                                if p.bit_length() + q.bit_length() == keysize:
                                    try:
                                        result = rsa_decrypt(p, q, ciphertext, j)
                                        if len(result) == 0 or result == "None":
                                            # indicates a failed decryption attempt
                                            sys.stdout.write('x')
                                        else:
                                            # SUCCESS! This is your decrypted message, sir...
                                            print "\n:: DECRYPTED::\n message = %s" % result
                                        # show all the p, q candidates just in case
                                        print "\np = %X\nq = %X\n" % (p, q)
                                    except Exception as e:
                                        print "ERROR: ", e # if cipher text length wrong, change decryption padding etc.
                                        pass # do nothing
    # finish with a counter summary
    print "count: %d  count2: %d  count3: %d\n\n" % (count, count2, count3)

def main():
    '''
    Scenario:

    Most of the information of an RSA private key has been lost, but we're able to extract only this:
    (i.e. output from the command: openssl rsa -in helloworld.key -text -noout)

    exponent1:
    69:8a:cf:cb:5a:5d:d4:ca:b7:09:6d:fe:da:94:75:
    c7:80:c1:aa:d4:66:dc:75:35:b6:c7:91:7b:d2:ae:
    6e:11:28:13:98:a0:29:47:8d:35:f8:e0:66:ca:8a:
    9f:59:a7:48:97:78:21:00:bb:4c:f6:06:76:68:81:
    5c:3f:00:81
    
    exponent2:
    00:94:79:94:5a:b5:4e:5c:d4:fa:c5:80:b6:75:01:
    03:0e:e3:3a:e1:6d:bb:05:9e:8a:1a:78:30:d4:88:
    d2:fa:1a:7e:3e:90:98:07:cb:d1:12:0a:b8:05:a1:
    b9:09:15:bd:d3:c8:76:ca:74:c1:32:ef:ae:05:6b:
    55:ad:3d:fb:61

    '''
    # these exponents above are below as dP and dQ
    sample_dp = 0x698acfcb5a5dd4cab7096dfeda9475c780c1aad466dc7535b6c7917bd2ae6e11281398a029478d35f8e066ca8a9f59a74897782100bb4cf6067668815c3f0081
    sample_dq = 0x009479945ab54e5cd4fac580b67501030ee33ae16dbb059e8a1a7830d488d2fa1a7e3e909807cbd1120ab805a1b90915bdd3c876ca74c132efae056b55ad3dfb61
    # this is an already encrypted file made, using
    # openssl rsautl -encrypt -in helloworld.txt -inkey helloworld.pub -pubin -out helloworld.enc
    sample_ciphertext = '9bccead296e0f33405ca8ee167ff366a95ac8cb667cfe2c7c5fcd10c2'\
                        '78962777f3583138fad52db987a4f7f6a10e8798330151a816bc32a20'\
                        'b4d9c82f512027cd4c817cbf3399bde736935ebf7404308eb7419fcc3'\
                        'b7ace7841e8f8a28cd8c5e7c5b90e6b0a32a03ff4e5392b044caf851a'\
                        '0fccc615da166c68495d8f1b7a7e'
    sample_filename = 'helloworld.enc'
    # write the sample encrypted file to disk
    if not os.path.isfile(sample_filename):
        with open('helloworld.enc', 'w') as f:
            f.write(binascii.unhexlify(sample_ciphertext))
    # read the file in, for whatever reason I had much better luck always reading the file in!
    ciphertext = open('helloworld.enc').read()
    # Here is where the magic happens...
    rsa_recovery(sample_dp, sample_dq, ciphertext, keysize=1024, start=65537)
    # IMPORTANT: If you have a publicExponent (e) that is not assumed to be 0x10001 (65537)
    # you will probably want to change start to start=3 above. 3, 17, 65537 are the most common 'e' used.

if __name__ == '__main__':
    main()