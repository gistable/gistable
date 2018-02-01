#!/usr/bin/env python
#
# Encrypts/decrypts data with salted ARC4 cipher.
#
# Implementation uses a randomly generated salt appended to the beginning of
# ciphertext. Arc4 key is mounted by digesting password and salt with SHA-1.
#

from random import randrange
from hashlib import sha1

__all__ = ['Arc4Salted']


class Arc4Salted(object):
    """Encrypts/decrypts streams with salted ARC4 cipher.
    Implementation uses a randomly generated salt appended to the beginning of ciphertext. Arc4 key is mounted by digesting password and salt with SHA-1.
    """

    def __init__(self, password, salt_len=16):
        if isinstance(password, file):
            password = password.read()
        self.password = password
        self.salt_len = salt_len

    def _crypt(self, str_or_stream, salt):
        key = sha1(self.password + salt).digest()
        x = 0
        box = range(256)
        for y in range(256):
            x = (x + box[y] + ord(key[y % 20])) % 256
            box[y], box[x] = box[x], box[y]
        x = y = 0
        for char in str_or_stream:
            x = (x + 1) % 256
            y = (y + box[x]) % 256
            box[x], box[y] = box[y], box[x]
            yield chr(ord(char) ^ box[(box[x] + box[y]) % 256])

    def encrypt(self, str_or_stream):
        salt = ''
        for _ in range(self.salt_len):
            salt += chr(randrange(256))
        for char in salt:
            yield char
        for e in self._crypt(str_or_stream, salt):
            yield e

    def decrypt(self, str_or_stream):
        salt = ''
        stream = iter(str_or_stream)
        for _ in range(self.salt_len):
            salt += stream.next()
        for e in self._crypt(stream, salt):
            yield e


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description="""Encrypts/decrypts files with salted ARC4 cipher.
    Implementation uses a randomly generated salt appended to the beginning of ciphertext. Arc4 key is mounted by digesting password and salt with SHA-1.
    """)
    parser.add_argument('function', metavar='(encrypt|decrypt)', type=str,
                        choices=['encrypt', 'decrypt'],
                        help='function to be executed (encrypt or decrypt)')
    parser.add_argument('-p', metavar='<string>', type=str, dest='password',
                        help='password', required=1)
    parser.add_argument('-i', metavar='<file>', type=str, dest='input',
                        help='input file', required=1)
    parser.add_argument('-o', metavar='<file>', type=str, dest='output',
                        help='output file', required=1)
    parser.add_argument('-s', metavar='<int>', type=int, default=16, dest='salt',
                        help='salt length (defaults to 16)')

    args = parser.parse_args()
    cipher = Arc4Salted(args.password, args.salt)

    if args.function == 'encrypt':
        with open(args.input, 'rb') as f:
            result = cipher.encrypt(f.read())
        with open(args.output, 'wb') as f:
            f.write(''.join(result))
    elif args.function == 'decrypt':
        with open(args.input, 'rb') as f:
            result = cipher.decrypt(f.read())
        with open(args.output, 'wb') as f:
            f.write(''.join(result))
