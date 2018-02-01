# -*- coding: utf-8 -*-

"""Part of an answer to http://stackoverflow.com/questions/7296535/easy-to-use-python-encryption-library-wrapper/7296656#7296656"""

import hashlib
import hmac
import os
import random
from Crypto.Cipher import AES


class AuthenticationError(Exception):
    pass


class MagicCrypt(object):
    
    AES_BLOCK_SIZE = 32
    SIG_SIZE = hashlib.sha256().digest_size
    
    def __init__(self, key):
        self.key = self._hash_key(key)
    
    def _hash_key(self, key):
        """Return a key suitable for use with the cipher"""
        return hashlib.sha256(key).digest()
    
    def _initialisation_vector(self):
        """get a random initialisation vector"""
        return os.urandom(16)
    
    def _cipher(self, key, iv):
        """Return a cipher. An object that implements .encrypt() and 
        .decrypt()
        """
        return AES.new(key, AES.MODE_CBC, iv)    
    
    def encrypt(self, data):
        iv = self._initialisation_vector()
        cipher = self._cipher(self.key, iv)
        ## get the required padding length
        pad = self.AES_BLOCK_SIZE - len(data) % self.AES_BLOCK_SIZE
        ## pad the data by appending repeate char    
        data = data + pad * chr(pad)
        ## encrypt and prepend the initialisation vector
        data = iv + cipher.encrypt(data)
        ## hash the encrypted data
        sig = hmac.new(self.key, data, hashlib.sha256).digest()
        ## append the hash to the data
        return data + sig
    
    def decrypt(self, data):
        ## extract the hash
        sig = data[-self.SIG_SIZE:]
        data = data[:-self.SIG_SIZE]
        ## check the encrypted data is valid using the hmac hash
        if hmac.new(self.key, data, hashlib.sha256).digest() != sig:
            raise AuthenticationError("message authentication failed")
        ## extract the initialisation vector
        iv = data[:16]
        data = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ## decrypt
        data = cipher.decrypt(data)
        ## remove the padding
        return data[:-ord(data[-1])]



if __name__ == '__main__':
    s = 'This is a secret'
    crypt = MagicCrypt('mypassword')
    encrypted = crypt.encrypt(s)
    decrypted = crypt.decrypt(encrypted)
    print decrypted == s