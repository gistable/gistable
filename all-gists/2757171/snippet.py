#!/usr/bin/env python
import base64, hashlib, hmac, json, sys, getpass
from Crypto.Cipher import AES
from Crypto.Hash import RIPEMD, SHA256

base58_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def prompt(p):
    return getpass.getpass(p + ": ")

def decrypt(encrypted, password):
    encrypted = base64.b64decode(encrypted)
    iv, encrypted = encrypted[:16], encrypted[16:]
    aeshash = pbkdf2(password, iv, 10, 32)
    clear = remove_iso10126_padding(AES.new(aeshash, AES.MODE_CBC, iv).decrypt(encrypted))
    return clear

def remove_iso10126_padding(s):
    ba = bytearray(s)
    pad_len = ba[-1]
    return str(ba[:-pad_len])

def base58_decode(v):
  value = 0; ret = ''
  for c in v: value = value*58 + base58_chars.find(c)
  for i in range(32):
      ret = "%c"%(value%256) + ret; value /= 256
  return ret

def base58_encode(v):
    value = 0; ret = ''
    for c in v: value = value*256 + ord(c)
    while value > 0:
        ret = base58_chars[value%58] + ret; value /= 58
    return ret

def to_sipa(s):
    version = 128 # or 239 for testnet
    key = chr(version) + base58_decode(s)
    return base58_encode(key + SHA256.new(SHA256.new(key).digest()).digest()[:4])

# pbkdf2 from http://matt.ucc.asn.au/src/pbkdf2.py

from struct import pack

# this is what you want to call.
def pbkdf2( password, salt, itercount, keylen, hashfn = hashlib.sha1 ):
    digest_size = hashfn().digest_size

    # l - number of output blocks to produce
    l = keylen / digest_size
    if keylen % digest_size != 0:
        l += 1

    h = hmac.new( password, None, hashfn )

    T = ""
    for i in range(1, l+1):
        T += pbkdf2_F( h, salt, itercount, i )

    return T[0: keylen]

def xorstr( a, b ):
    if len(a) != len(b):
        raise "xorstr(): lengths differ"

    ret = ''
    for i in range(len(a)):
        ret += chr(ord(a[i]) ^ ord(b[i]))

    return ret

def prf( h, data ):
    hm = h.copy()
    hm.update( data )
    return hm.digest()

# Helper as per the spec. h is a hmac which has been created seeded with the
# password, it will be copy()ed and not modified.
def pbkdf2_F( h, salt, itercount, blocknum ):
    U = prf( h, salt + pack('>i',blocknum ) )
    T = U

    for i in range(2, itercount+1):
        U = prf( h, U )
        T = xorstr( T, U )

    return T

clear = decrypt(prompt("encrypted wallet"), prompt("password"))
obj = json.loads(clear)

if (obj.has_key('double_encryption')):
    print("wallet uses double encryption")
    password = obj['sharedKey'].encode('ascii') + prompt("2nd password")
    for key in obj['keys']: key['priv'] = decrypt(key['priv'], password)
for key in obj['keys']: key['priv_sipa'] = to_sipa(key['priv'])
print(json.dumps(obj, indent=4, sort_keys = True))