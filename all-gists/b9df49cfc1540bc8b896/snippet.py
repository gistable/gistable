# requires https://github.com/mitchellrj/python-pgp
from pgp.packets import constants
from pgp.packets import parsers
from Crypto.PublicKey import RSA
import sys

"""
Converts an GnuPG key to a PEM key
If the input is password protected, the same password will be used to protect 
the PEM output.
"""
def convert(keyid, passphrase, infh, outfh):
    packets = parsers.parse_binary_packet_stream(infh)
    for packet in packets:
        if packet.type == constants.SECRET_KEY_PACKET_TYPE or packet.type == constants.SECRET_SUBKEY_PACKET_TYPE:
            print('found key id', packet.key_id)
            if packet.key_id != keyid:
                continue
            if passphrase is not None:
                print('decrypting key', packet.key_id)
                packet.decrypt(passphrase)
            print('creating PEM')
            rsa = RSA.construct((packet.modulus, packet.exponent, packet.exponent_d, packet.prime_p, packet.prime_q, packet.multiplicative_inverse_u))
            pem = rsa.exportKey('PEM', passphrase, 1)
            outfh.write(pem)
            return
        elif packet.type == constants.PUBLIC_KEY_PACKET_TYPE or packet.type == constants.PUBLIC_SUBKEY_PACKET_TYPE:
            print('found public key id', packet.key_id)
            if packet.key_id != keyid:
                continue
            print('creating PEM')
            rsa = RSA.construct((packet.modulus, packet.exponent))
            pem = rsa.exportKey('PEM')
            outfh.write(pem)
            return
    print('key not found')

def main(argv):
    if (len(argv) < 3):
        print('usage: gpg_to_pem.py keyid input.gpg output.pem [passphrase]')
        return
    with open(argv[1], 'rb') as infh:
        with open(argv[2], 'wb') as outfh:
            passphrase = bytes(argv[3], 'ascii') if len(argv) > 3 else None
            convert(argv[0].upper(), passphrase, infh, outfh)

if __name__ == "__main__":
    main(sys.argv[1:])
