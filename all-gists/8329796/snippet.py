#!/usr/bin/python

import os
import hashlib
import getpass
import base64

password1 = None
password2 = None

# Read the password
while password1 != password2 or password1 == None:
  password1 = getpass.getpass()
  password2 = getpass.getpass("Confirm password: ")
  if (password1 != password2):
    print "\nPassword mismatch, try again."

# Generate a 5 byte random salt
salt = os.urandom(5)

# Hash our password + salt
sha = hashlib.sha512()
sha.update(password1)
sha.update(salt)
ssha512 = base64.b64encode('{}{}'.format(sha.digest(), salt))

# Print it out with a prefix for Dovecot
print "\n{{SSHA512}}{}".format(ssha512)
