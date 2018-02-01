#!/usr/bin/env python
"""
Simple chosen-plaintext attack on AES-CTR given NONCE and IV re-use for
multiple ciphertexts

Copyleft 2011 Ian Gallagher <crash@neg9.org>
"""
import sys

def decrypt(keystream, ciphertext):
    """
    Given an ordinal list of keystream bytes, and an ordinal list of
    ciphertext, return the binary plaintext string after decryption
    (standard XOR - applicable for AES-CTR mode, etc.)
    """
    pt = ''
    for pos in xrange(len(ciphertext)):
        if pos >= len(keystream):
            print >>sys.stderr, "Ran out of keystream material at pos = %d" % pos
            break
        else:
            pt += chr(ciphertext[pos] ^ keystream[pos])
    return(pt)

def derivekeystream(chosen_ciphertext, chosen_plaintext):
    """
    Given an ordinal list of a chosen plaintext and the corrosponding chosen
    ciphertext, derive AES-CTR keystream and return it as an ordinal list
    """
    return map(lambda x: x[0] ^ x[1], zip(map(ord, chosen_ciphertext), map(ord, chosen_plaintext)))

def main():
    """
    chosen_ciphertext and target_ciphertext should be in the binary encrypted
    format, so prepare it by base64 decoding it, or whatever.

    chosen_plaintext should be in the resulting binary/ASCII format of the
    origial data.
    """
    chosen_plaintext = ''
    chosen_ciphertext = ''

    keystream = derivekeystream(chosen_ciphertext, chosen_plaintext)
    target_ciphertext = sys.argv[1]

    print decrypt(keystream, map(ord, target_ciphertext))

if '__main__' == __name__:
	main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4