#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import base64
import random
import hashlib
import os


class AesCrypt256:
    """
    Aes Crypter based on pyCrypto
    will replace Lib/Norris/AesCrypter.py

    >>> c = AesCrypt256()
    >>> key = 'mysecret'
    >>> text = 'foobar'
    >>> c.decrypt(key,c.encrypt(key,text))
    'foobar'

    >>> c.decryptB64(key,c.encryptB64(key,text))
    'foobar'
    
    >>> c.pkcs5_unpad(c.pkcs5_pad('foobar'))
    'foobar'

    >>> c.pkcs5_unpad(c.pkcs5_pad('foobar-'*10))
    'foobar-foobar-foobar-foobar-foobar-foobar-foobar-foobar-foobar-foobar-'
    """
    
    BLOCK_SIZE = 32

    def pkcs5_pad(self,s):
        """
        padding to blocksize according to PKCS #5
        calculates the number of missing chars to BLOCK_SIZE and pads with
        ord(number of missing chars)
        @see: http://www.di-mgt.com.au/cryptopad.html


        @param s: string to pad
        @type s: string

        @rtype: string
        """
        return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)

    def pkcs5_unpad(self,s):
        """
        unpadding according to PKCS #5

        @param s: string to unpad
        @type s: string

        @rtype: string
        """
        return s[0:-ord(s[-1])]


    def encrypt(self, key, value):
        """Encrypt value by key

        @param key: key to encrypt with
        @type key: string

        @param value: value to encrypt
        @type value: string

        @rtype: string
        """

        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        key = hashlib.sha256(key).digest()[:self.BLOCK_SIZE]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        crypted = cipher.encrypt(self.pkcs5_pad(value))
        return iv+crypted


    def decrypt(self, key, value):
        """Decrypt value by key

        @param key: key to decrypt with
        @type key: string

        @param value: value to decrypt
        @type value: string

        @rtype: string
        """
        key = hashlib.sha256(key).digest()[:self.BLOCK_SIZE]
        iv = value[:16]
        crypted = value[16:]
        cipher = AES.new(key,AES.MODE_CBC,iv)
        return self.pkcs5_unpad(cipher.decrypt(crypted))

    def encryptB64(self, key, value):
        """Encrypt and return in base64

        @param key: key to encrypot with
        @type key: string

        @param value: value to encrypt
        @type value: string

        @rtype: string
        """
        return base64.b64encode(self.encrypt(key, value))

    def decryptB64(self, key, value):
        """decrypt from base64

        @param key: key to decrypt with
        @type key: string

        @param value: value to decrypt in base64
        @type value: string

        @rtype: string
        """        
        return self.decrypt(key,base64.b64decode(value))
    

    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
