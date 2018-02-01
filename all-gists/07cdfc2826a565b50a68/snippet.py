# Inspired and adopted from https://gist.github.com/sekondus/4322469
# COMES WITH ABOSLUTELY NO WARRANTY OF ANY KIND.
# TOTAL FREEWARE, NO CLAIMS MADE OF ANY SORT.
# SELL IT, BURN IT, PRETEND ITS YOUR OWN.
# RELEASED UNDER NOBODY CARES LICENSE.

import os
import base64

from Crypto.Cipher import AES



BLOCK_SIZE = 32
PADDING='#'

def _pad(data, pad_with=PADDING):
    """
    Data to be encrypted should be on 16, 24 or 32 byte boundaries.
    So if you have 'hi', it needs to be padded with 30 more characters 
    to make it 32 bytes long. Similary if something is 33 bytes long, 
    31 more bytes are to be added to make it 64 bytes long which falls 
    on 32 boundaries.

    - BLOCK_SIZE is the boundary to which we round our data to.
    - PADDING is the character that we use to padd the data.
    """
    return data + (BLOCK_SIZE - len(data) % BLOCK_SIZE) * PADDING

def encrypt(secret_key, data):
    """
    Encrypts the given data with given secret key. 
    """
    cipher = AES.new(_pad(secret_key, '@')[:32])
    return base64.b64encode(cipher.encrypt(_pad(data)))

def decrypt(secret_key, encrypted_data):
    """
    Decryptes the given data with given key.
    """
    cipher = AES.new(_pad(secret_key, '@')[:32])
    return cipher.decrypt(base64.b64decode(encrypted_data)).rstrip(PADDING)


KEY='your-key-super-duper-secret-key-here-only-first-32-characters-are-used'
decrypted =  encrypt(KEY, 'Hello, world!')
print decrypted
print decrypt(KEY, decrypted)
