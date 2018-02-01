#!/usr/bin/env python3

# CodeIgniter pre-2.2 non-mcrypt Encrypt reverser.
# Finds the key by partially-known plaintext attack.
# Written by Yuki Izumi.  Placed in the public domain.

import codecs
import re
import sys
import time


def decode(s, key):
    r = bytearray()
    for i in range(len(s) // 2):
        r.append(s[i*2] ^ s[i*2+1] ^ key[(i*2)%40] ^ key[(i*2+1)%40])
    return bytes(r)


def find_key(known, encrypted):
    key = bytearray(b'0') * 40
    confirmed = [False] * 20

    hexstr = b'0123456789abcdef'

    ix = 0
    while not all(confirmed):
        if confirmed[ix%20]:
            ix += 1
            continue

        kcompb = known[ix::20]

        for k in range(256):
            key[(ix*2)%40] = hexstr[k&0xf]
            key[(ix*2+1)%40] = hexstr[k>>4]
            r = decode(encrypted, key)

            kcomp = kcompb
            rcomp = r[ix::20][:len(kcomp)]

            while True:
                try:
                    j = kcomp.index(b' ')
                except ValueError:
                    break
                kcomp = kcomp[:j] + kcomp[j+1:]
                rcomp = rcomp[:j] + rcomp[j+1:]

            if kcomp[0] == rcomp[0]:
                confirmed[ix%20] = True
                break

        if not confirmed[ix%20]:
            return None

        ix += 1

    return key


with open(sys.argv[1], 'r') as f:
    encrypted = f.read().split("\n", 2)[0]

encrypted = codecs.decode(encrypted.encode('ascii'), 'base64')

# Try each of these; space represents an unknown value.  Here we account for
# the unknown size of the session array in general.  We just need one byte of
# known plaintext for each index of the key, i.e. as long as there's at least
# one value in each 'column'.
knowns = ([
    b'a: :{s:10:"session_i' +
    b'd";s:32:"           '
,
    b'a:  :{s:10:"session_' +
    b'id";s:32:"          '
,
    b'a:   :{s:10:"session' +
    b'_id";s:32:"         '
])

key = None
for known in knowns:
    key = find_key(known, encrypted)
    if key:
        break

if not key:
    print("Could not recover key.")
    exit(1)

print(key.decode('ascii'))
print(decode(encrypted, key))