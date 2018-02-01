#!/usr/bin/env python
#-*- coding: utf-8 -*-
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
import base64
import StringIO

# passphrase, random string => private key, public key pair
# encrypt with public key
# decrypt with pem, passphrase

def gen_key_pair(passpharse):
    random_generator = Random.new().read
    key = RSA.generate(2048, random_generator)
    return key.exportKey(passphrase=passphrase), key.publickey().exportKey()

def rsa_encrypt(message, pub):
    keystream = StringIO.StringIO(pub)
    pubkey = RSA.importKey(keystream.read())
    h = SHA.new(message)
    cipher = PKCS1_v1_5.new(pubkey)
    return base64.encodestring(cipher.encrypt(message+h.digest()))

def rsa_decrypt(ciphertext, pem, passphrase):
    ciphertext = base64.decodestring(ciphertext)
    keystream = StringIO.StringIO(pem)
    pemkey = RSA.importKey(keystream.read(), passphrase=passphrase)
    dsize = SHA.digest_size
    sentinel = Random.new().read(15+dsize)
    cipher = PKCS1_v1_5.new(pemkey)
    message = cipher.decrypt(ciphertext, sentinel)
    digest = SHA.new(message[:-dsize]).digest()
    if digest == message[-dsize:]:
        return message[:-dsize]
    else:
        raise ValueError('Cannot decrypt message')


if __name__ == '__main__':
    message = 'To be encrypted'
    passphrase = 'Your Passphrase'

    pem, pub = gen_key_pair(passphrase)
    print 'Private Key:\n%s\n' % pem
    print 'Public Key:\n%s\n' % pub

    encdata = rsa_encrypt(message, pub)
    print 'Encrypted Message:\n', encdata

    decdata = rsa_decrypt(encdata, pem, passphrase)
    print 'Decrypted Message:\n', decdata
