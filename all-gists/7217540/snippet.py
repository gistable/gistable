#!/usr/bin/env python
"""
http://www.openldap.org/faq/data/cache/347.html

As seen working on Ubuntu 12.04 with OpenLDAP 2.4.28-1.1ubuntu4

Author: Roberto Aguilar <roberto@baremetal.io>
"""
import hashlib
import os


def check_password(tagged_digest_salt, password):
    """
    Checks the OpenLDAP tagged digest against the given password
    """
    # the entire payload is base64-encoded
    assert tagged_digest_salt.startswith('{SSHA}')

    # strip off the hash label
    digest_salt_b64 = tagged_digest_salt[6:]

    # the password+salt buffer is also base64-encoded.  decode and split the
    # digest and salt
    digest_salt = digest_salt_b64.decode('base64')
    digest = digest_salt[:20]
    salt = digest_salt[20:]

    sha = hashlib.sha1(password)
    sha.update(salt)

    return digest == sha.digest()


def make_secret(password):
    """
    Encodes the given password as a base64 SSHA hash+salt buffer
    """
    salt = os.urandom(4)

    # hash the password and append the salt
    sha = hashlib.sha1(password)
    sha.update(salt)

    # create a base64 encoded string of the concatenated digest + salt
    digest_salt_b64 = '{}{}'.format(sha.digest(), salt).encode('base64').strip()

    # now tag the digest above with the {SSHA} tag
    tagged_digest_salt = '{{SSHA}}{}'.format(digest_salt_b64)

    return tagged_digest_salt


if __name__ == '__main__':
    # buffer straight out of OpenLDAP
    ldap_buf = 'e1NTSEF9VGY1dVFxUkl0VzV2NGowV0RNNXczY2dJd2ZLS0FUcFg='
    print 'ldap buffer result: {}'.format(check_password(ldap_buf, 'foobar'))

    # check that make_secret() above can properly encode
    print 'checking make_secret: {}'.format(check_password(make_secret('foobar'), 'foobar'))
