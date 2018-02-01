"""
DrupalPasswordHasher

To use, put this in any app and add to your settings.py, something like this:

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'myproject.myapp.drupal_hasher.DrupalPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

Three notes:

-This requires Drupal 1.4 or higher (with the introduction of the flexible password
hasher)

-In Drupal, the number of algorithm iterations is a power of 2,
which is represented by the first character after the $. Specifically, it
performs 2^(index within _ITOA64) iterations, such that 'C' represents 2^14
and 'D' would represent 2^15.

-In Drupal the passwords are stored as:

$S$<hash>

while in Django the passwords are stored as

S$<hash>

So you must cut off the first character of each password when migrating.
"""

import hashlib

from django.contrib.auth.hashers import BasePasswordHasher

_ITOA64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


class DrupalPasswordHasher(BasePasswordHasher):
    algorithm = "S"
    iter_code = 'C'
    salt_length = 8

    def encode(self, password, salt, iter_code=None):
        """The Drupal 7 method of encoding passwords"""
        if iter_code == None:
            iterations = 2 ** _ITOA64.index(self.iter_code)
        else:
            iterations = 2 ** _ITOA64.index(iter_code)
        hash = hashlib.sha512(salt + password).digest()

        for i in range(iterations):
            hash = hashlib.sha512(hash + password).digest()

        l = len(hash)

        output = ''
        i = 0

        while i < l:
            value = ord(hash[i])
            i = i + 1

            output += _ITOA64[value & 0x3f]
            if i < l:
                value |= ord(hash[i]) << 8

            output += _ITOA64[(value >> 6) & 0x3f]
            if i >= l:
                break
            i += 1

            if i < l:
                value |= ord(hash[i]) << 16

            output += _ITOA64[(value >> 12) & 0x3f]
            if i >= l:
                break
            i += 1

            output += _ITOA64[(value >> 18) & 0x3f]

        longhashed = "%s$%s%s%s" % (self.algorithm, iter_code,
                                    salt, output)
        return longhashed[:54]

    def verify(self, password, encoded):
        hash = encoded.split("$")[1]
        iter_code = hash[0]
        salt = hash[1:1 + self.salt_length]
        return encoded == self.encode(password, salt, iter_code)
