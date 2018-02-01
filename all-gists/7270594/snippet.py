#!/usr/bin/env python
import hashlib
import optparse

import paramiko
from Crypto.PublicKey import RSA


def insert_char_every_n_chars(string, char='\n', every=64):
    return char.join(
        string[i:i + every] for i in xrange(0, len(string), every))


def get_rsa_key(key_location=None, key_file_obj=None, passphrase=None,
                use_pycrypto=False):
    key_fobj = key_file_obj or open(key_location)
    try:
        if use_pycrypto:
            key = RSA.importKey(key_fobj, passphrase=passphrase)
        else:
            key = paramiko.RSAKey.from_private_key(key_fobj,
                                                   password=passphrase)
        return key
    except (paramiko.SSHException, ValueError):
        raise Exception(
            "Invalid RSA private key file or missing passphrase: %s" %
            key_location)


def get_public_key(key):
    return ' '.join([key.get_name(), key.get_base64()])


def generate_rsa_key():
    return paramiko.RSAKey.generate(2048)


def get_private_rsa_fingerprint(key_location=None, key_file_obj=None,
                                passphrase=None):
    """
    Returns the fingerprint of a private RSA key as a 59-character string (40
    characters separated every 2 characters by a ':'). The fingerprint is
    computed using the SHA1 (hex) digest of the DER-encoded (pkcs8) RSA private
    key.
    """
    k = get_rsa_key(key_location=key_location, key_file_obj=key_file_obj,
                    passphrase=passphrase, use_pycrypto=True)
    sha1digest = hashlib.sha1(k.exportKey('DER', pkcs=8)).hexdigest()
    fingerprint = insert_char_every_n_chars(sha1digest, ':', 2)
    print '>>> RSA Private Key Fingerprint:\n%s' % fingerprint
    return fingerprint


def get_public_rsa_fingerprint(key_location=None, key_file_obj=None,
                               passphrase=None):
    """
    Returns the fingerprint of the public portion of an RSA key as a
    47-character string (32 characters separated every 2 characters by a ':').
    The fingerprint is computed using the MD5 (hex) digest of the DER-encoded
    RSA public key.
    """
    privkey = get_rsa_key(key_location=key_location, key_file_obj=key_file_obj,
                          passphrase=passphrase, use_pycrypto=True)
    pubkey = privkey.publickey()
    md5digest = hashlib.md5(pubkey.exportKey('DER')).hexdigest()
    fingerprint = insert_char_every_n_chars(md5digest, ':', 2)
    print '>>> RSA Public Key Fingerprint:\n%s' % fingerprint
    return fingerprint


def main():
    usage = 'usage: ec2fingerprint [options] <rsakey>'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--public-only", dest="public_only",
                      action="store_true",
                      default=False)
    parser.add_option("-P", "--private-only", dest="private_only",
                      action="store_true",
                      default=False)
    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error("please specify a single RSA private key file")
    path = args[0]
    if opts.public_only:
        get_public_rsa_fingerprint(key_location=path)
    elif opts.private_only:
        get_private_rsa_fingerprint(key_location=path)
    else:
        get_public_rsa_fingerprint(key_location=path)
        print
        get_private_rsa_fingerprint(key_location=path)


if __name__ == '__main__':
    main()
