#!/usr/bin/python
# coding=utf-8

# sha256frompubkey.py: Displays SHA256 fingerprint of public key in Python 2/3.

# Modified by Steven Maude from
# https://github.com/joyent/python-manta/blob/4de7445277c0971c7ff43ef246018d055ef21d20/manta/auth.py
# MIT licence.

# Usage: obtain a public key using ssh-keyscan <host> > key.pub
#        then sha256frompubkey.py `cut -f3 -d " " key.pub`
import base64
import binascii
import hashlib
import re
import sys


def sha256_fingerprint_from_pub_key(data):
    data = data.strip()

    # accept either base64 encoded data or full pub key file,
    # same as `fingerprint_from_ssh_pub_key
    if (re.search(r'^ssh-(?:rsa|dss) ', data)):
        data = data.split(None, 2)[1]
    
    # Python 2/3 hack. May be a better solution but this works.
    try:
        data = bytes(data, 'ascii')
    except TypeError:
        data = bytes(data)

    digest = hashlib.sha256(binascii.a2b_base64(data)).digest()
    encoded = base64.b64encode(digest).rstrip(b'=')  # ssh-keygen strips this
    return "SHA256:" + encoded.decode('utf-8')


def main():
    print(sha256_fingerprint_from_pub_key(sys.argv[1]))

if __name__ == '__main__':
    main()