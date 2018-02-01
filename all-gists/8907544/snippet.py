# -*- coding: utf-8 -*-
import sys
import os
import base64
import bcrypt
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

class Blockout:

    @staticmethod
    def enblockout(s, key):
        # user provided
        return
    
    @staticmethod
    def deblockout(blockout, key):
        # user provided
        return

    @staticmethod
    def hash(s):
        # bcrypt for password hashing with complexity 12
        return bcrypt.hashpw(s, bcrypt.gensalt(12))

    @staticmethod
    def hash_verify(s, hashed):
        return bcrypt.hashpw(s, hashed) == hashed

    @staticmethod
    def hash_to_aes256_key(hashed):
        # return binary NOT hex digest
        sha256 = SHA256.new(hashed)
        return sha256.digest()
    
    @staticmethod
    def encrypt(s, key):

        # pad the s to block size boundary
        s_padding_len = AES.block_size - (len(s) % AES.block_size)
        s += chr(0)*s_padding_len

        # create a random iv
        iv = Random.new().read(AES.block_size)

        # AES encrypt
        aes = AES.new(key, AES.MODE_CBC, iv)
        encrypted = aes.encrypt(s)

        # return the encrypted and iv
        data = {"encrypted": base64.b64encode(encrypted), "iv": base64.b64encode(iv)}
        return data

    @staticmethod
    def decrypt(s, key, iv):

        # base64 decode s
        s = base64.b64decode(s)

        # base64 decode the iv
        iv = base64.b64decode(iv)

        # AES decrypt using CBC
        aes = AES.new(key, AES.MODE_CBC, iv)
        decrypted = aes.decrypt(s)

        # return depaded decrypted
        return decrypted.strip()
        
def main():
    
    # aes256 encryption algorithm
    # 1.  bcrypt the password (to secure the password)
    # 2.  sha256 the bcrypted password (only to get a fixed 256 bit size for aes 256)
    # 3.  generate a random IV
    # 3.  aes256 encrypt the message with the sha256 hash of the bcrypted password and IV in CBC mode
    # 4.  base64 encode the encrypted message and IV for storage

    # aes256 decryption algorithm
    # 1.  base64 decode the encrypted messaged and IV
    # 2.  use the sha256 bcrypted password as the aes256 key
    # 3.  aes256 decrypt the message with the sha256 hash of the bcrypted password, IV, in CBC mode
    # 4.  trim any padding

    # bcrypt hash the key
    keyHash = Blockout.hash("password")
    print "keyHash: " + keyHash + "\n"

    # convert the key hash to AES256 key
    aesKey = Blockout.hash_to_aes256_key(keyHash)
    print "aesKey: " + aesKey

    # aes256 encrypt using aesKey
    data = Blockout.encrypt("hello", aesKey)
    print "data: "
    print data 
    print "\n"

    # aes256 decrypt 
    s = Blockout.decrypt(data["encrypted"], aesKey, data["iv"])
    print "s: " + s + "\n"
        
# execute main
if __name__ == "__main__":
    main()