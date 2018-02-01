#!/usr/bin/env python
import base64
import hashlib
import subprocess
import sys

B32ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

def luhn_checksum(data, alphabet=B32ALPHABET):
    n = len(alphabet)
    number = tuple(alphabet.index(i) for i in reversed(data))
    result = (sum(number[::2]) +
              sum(sum(divmod(i * 2, n)) for i in number[1::2])) % n
    return alphabet[-result]

def main(incert):
    der_data = subprocess.check_output(['openssl', 'x509', '-outform', 'DER'], stdin=incert)
    data_hash = hashlib.sha256(der_data)
    b32_hash = base64.b32encode(data_hash.digest()).decode('ascii')

    result = b32_hash.upper().rstrip('=')
    blocks = [result[pos:pos+13] for pos in range(0, len(result), 13)]
    result = ''.join(block + luhn_checksum(block) for block in blocks)

    blocks = [result[pos:pos+7] for pos in range(0, len(result), 7)]
    print('-'.join(blocks))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate syncthing ID from certificate')
    parser.add_argument('incert', type=argparse.FileType('rb'), help='Certificate path')
    args = parser.parse_args()
    main(**vars(args))
