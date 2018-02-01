import hashlib
import base64
import argparse
import sys

from Crypto.PublicKey import RSA


def calculate_onion(pem_key):
    key = RSA.importKey(pem_key)
    if key.has_private():
        key = key.publickey()

    onion_address = hashlib.sha1(key.exportKey('DER')).digest()[:10]
    return base64.b32encode(onion_address).decode('utf-8').lower()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="%s calculates the onion address from a hidden service "
        "descriptor or public key.")
    parser.add_argument("file", help="Descriptor or PEM encoded public key.")
    args = parser.parse_args()

    # Load the descriptor or public key
    with open(args.file, 'r') as descriptor:
        descriptor = descriptor.read()

    # Read the PEM encoded key block
    in_key = False
    public_key = ''
    for line in descriptor.split('\n'):
        if line == '-----BEGIN RSA PUBLIC KEY-----':
            in_key = True
        if in_key:
            public_key += line.strip() + '\n'
        if line == '-----END RSA PUBLIC KEY-----':
            break

    if not public_key:
        print('No public key block found')
        sys.exit(1)

    onion_address = calculate_onion(public_key)
    print('Onion Address: %s.onion' % onion_address)
