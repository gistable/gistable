#!/usr/bin/env python

# Python script to decrypt encrypted ENEX notes exported from Evernote as ENEX
#
# This will onle work on notes encypted after 2014 using the "ENC0" format
#
# This script requires a modified version of pbkdf2.py to support SHA256
#  https://github.com/PaulUithol/python-pbkdf2
#
# There's no helpful error if your password was incorrect, it will just
# echo stdin to stdout unchanged
#
# This will only decrypt the last encrypted section of the file, if there are
# multiple sections pipe the output back into the script
#
# The encryption method is described by Evernote here:
#  https://help.evernote.com/hc/en-us/articles/208314128
#
# The byte-format of the ENC0 scheme is described here:
#  http://soundly.me/decoding-the-Evernote-en-crypt-field-payload/
#
# 2016-12-18 Lee Maguire

import getopt
import sys
import re
import base64
import hmac
import hashlib

from pbkdf2 import PBKDF2
from Crypto.Cipher import AES

password = b'swordfish'  # It's the name of a fish

keylength = 128
iterations = 50000

opts, args = getopt.getopt(sys.argv[1:],"hp:",["password="])
for opt, arg in opts:
  if opt == '-h':
    print 'Usage: en-decrypt.py -p <password> < encrypted.enex > decrypted.enex'
    sys.exit()
  elif opt in ("-p", "--password"):
    password = arg

input_text = "".join(sys.stdin)
c = re.search(r"(?P<head>.*)(?P<crypt1><en-crypt .*>)(?P<b64>.*)(?P<crypt2></en-crypt>)(?P<tail>.*)", input_text, re.DOTALL)

if c:
  bintxt = base64.b64decode(c.group('b64'))
  salt = bintxt[4:20]
  salthmac = bintxt[20:36]
  iv = bintxt[36:52]
  ciphertext = bintxt[52:-32]
  body = bintxt[0:-32]
  bodyhmac = bintxt[-32:]

  ## use the password to generate a digest for the encrypted body
  ## if it matches the existing digest we can assume the password is correct
  keyhmac = PBKDF2(password, salthmac, iterations, hashlib.sha256).read(keylength/8)
  testhmac = hmac.new(keyhmac, body, hashlib.sha256)
  match_hmac = hmac.compare_digest(testhmac.digest(),bodyhmac)

  if match_hmac:
    key = PBKDF2(password, salt, iterations, hashlib.sha256).read(keylength/8)
    aes = AES.new(key, AES.MODE_CBC, iv)
    plaintext = aes.decrypt(ciphertext)
    sys.stdout.write( c.group('head') + plaintext + c.group('tail') )
  else:
    sys.stdout.write( input_text )
    sys.exit(1)
else:
  sys.stdout.write( input_text )
sys.exit(0)