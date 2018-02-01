#!/usr/bin/env python3

# original: https://raw.githubusercontent.com/tweksteen/jenkins-decrypt/master/decrypt.py
# requires: pycrypto


import re
import sys
import base64

from hashlib import sha256
from binascii import hexlify, unhexlify, Error as BAError

from Crypto.Cipher import AES

MAGIC = b'::::MAGIC::::'


def usage():
    print(sys.argv[0], "<master.key> <hudson.util.Secret>")
    sys.exit(0)


def get_key():
    master_key = open(sys.argv[1], 'r').read().encode('utf-8')
    hudson_secret_key = open(sys.argv[2], 'rb').read()

    hashed_master_key = sha256(master_key).digest()[:16]
    o = AES.new(hashed_master_key, AES.MODE_ECB)
    x = o.decrypt(hudson_secret_key)
    assert MAGIC in x

    k = x[:-16]
    return k[:16]


def decrypt(password_hash, key):
    p = base64.decodestring(password_hash.encode('utf-8'))
    o = AES.new(key, AES.MODE_ECB)
    x = o.decrypt(p)
    assert MAGIC in x

    return re.split(MAGIC.decode('utf-8'), x.decode('utf-8'), 1)[0]


def main():
    if len(sys.argv) != 3:
        usage()

    key = get_key()

    while True:
        try:
            password = input('Password-Hash: ')
            if not password:
                break
            else:
                print('Password:', decrypt(password, key))
        except (ValueError, BAError) as e:
            print('Error:', e)
        except (KeyboardInterrupt, EOFError):
            print()
            break


if __name__ == '__main__':
    main()