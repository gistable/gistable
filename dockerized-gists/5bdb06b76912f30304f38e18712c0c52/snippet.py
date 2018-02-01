#!/usr/bin/env python2.7

import math
import sys
import hashlib

__b32chars = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58encode(v):
  """ encode v, which is a string of bytes, to base58.
  """
  r1 = hashlib.sha256(v)
  r2 = hashlib.sha256(r1.digest())
  ch = r2.digest()[0:4]
  v += ch

  long_value = 0L
  for (i, c) in enumerate(v[::-1]):
    long_value += ord(c) << (8*i)

  result = ''
  while long_value >= 58:
    div, mod = divmod(long_value, 58)
    result = __b58chars[mod] + result
    long_value = div
  result = __b58chars[long_value] + result

  nPad = 0
  for c in v:
    if c == '\0': nPad += 1
    else: break
  result = (__b58chars[0]*nPad) + result

  return result

def b58decode(v):
  """ decode v into a string of len bytes
  """
  long_value = 0L
  for (i, c) in enumerate(v[::-1]):
    long_value += __b58chars.find(c) * (58**i)

  result = ''
  while long_value >= 256:
    div, mod = divmod(long_value, 256)
    result = chr(mod) + result
    long_value = div
  result = chr(long_value) + result

  nPad = 0
  for c in v:
    if c == __b58chars[0]: nPad += 1
    else: break

  result = (chr(0)*nPad + result)[:-4]

  return result.encode("hex_codec")

def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def bech32_polymod(values):
    c = 1
    for d in values:
        c0 = (c >> 35)
        c = ((c & 0x07ffffffff) << 5) ^ d
        c ^= 0x98f2bc8e61 if (c0 & 0x01) else 0
        c ^= 0x79b76d99e2 if (c0 & 0x02) else 0
        c ^= 0xf33e5fb3c4 if (c0 & 0x04) else 0
        c ^= 0xae2eabe2a8 if (c0 & 0x08) else 0
        c ^= 0x1e4f43e470 if (c0 & 0x10) else 0

    return (c ^ 1)

def b32chksum(v):
    data    = [ord(x) & 31 for x in "bitcoincash"] + [0] + v + [0,0,0,0,0,0,0,0]
    chk_int = bech32_polymod(data)
    chk_hex = format(chk_int, '010x')
    chk8bit = [int(chk_hex[i:i+2],16) for i in range(0,len(chk_hex),2)]
    return convertbits(chk8bit, 8, 5, True)

def b32encode(v):
    v8bit  = [int(v[i:i+2],16) for i in range(0,len(v),2)]
    v5bit  = convertbits(v8bit, 8, 5, True)
    v5bit += b32chksum(v5bit)
    bech32 = ''.join([__b32chars[d] for d in v5bit])
    return bech32

def b32decode(v):
    v5bit = [__b32chars.find(x) for x in v][:-8]
    v8bit = convertbits(v5bit, 5, 8, False)
    v_hex = (bytes(bytearray(v8bit))).encode("hex_codec")
    return v_hex

if __name__ == "__main__":

    if len(sys.argv) > 1:

        if sys.argv[1] == '-old':
            script = b58decode(sys.argv[2])
            if script[1] == '5':
                script = '08' + script[2:]
                print ("\"OP_HASH160 " + script[2:] + " OP_EQUAL\"")
            else:
                print ("\"OP_DUP OP_HASH160 " + script[2:] + " OP_EQUALVERIFY OP_CHECKSIG\"")
            print ("bitcoincash:" + b32encode(script))

        if sys.argv[1] == '-new':
            new = ((sys.argv[2])[12:]).lower()
            script = b32decode(new)
            if script[1] == '8':
                script = '05' + script[2:]
                print ("\"OP_HASH160 " + script[2:] + " OP_EQUAL\"")
            else:
                print ("\"OP_DUP OP_HASH160 " + script[2:] + " OP_EQUALVERIFY OP_CHECKSIG\"")
            print b58encode(script.decode("hex_codec"))

    else:
        print
        print 'Usage: ./conv.py {-old <oldaddress> | -new <newaddress>}'
        print
        print '       -old  converts base58 to bech32'
        print '       -new  converts bech32 to base58'
        print