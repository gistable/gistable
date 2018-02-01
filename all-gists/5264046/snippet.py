#Shamefully taken from http://www.codekoala.com/blog/2009/aes-encryption-python-using-pycrypto/ and adapted to python3
#Adapted to show the effect of an incorrect key
from Crypto.Cipher import AES
import base64
import os

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
def pad(s): 
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# encrypt with AES, encode with base64
def EncodeAES(plaindata, key):
    key = pad(key)
    cipher = AES.new(key)
    enc = cipher.encrypt(pad(plaindata))#cipher.encrypt(s)#
    return base64.b64encode(enc)

def DecodeAES(encodeddata, key): 
    key = pad(key)
    cipher = AES.new(key)
    b64 = base64.b64decode(encodeddata)
    return cipher.decrypt(b64)

# encode a string
encoded = EncodeAES('password', "1234")
print('Encrypted string:', encoded)

# decode the encoded string
print('Incorrectly decrypted string:', DecodeAES(encoded, "WRONGPASS"))
print('Correctly   decrypted string:', DecodeAES(encoded, "1234"))