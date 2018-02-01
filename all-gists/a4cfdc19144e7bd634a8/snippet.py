#!/usr/bin/python

import sys
import hashlib
from OpenSSL.crypto import *

def main():
  if(len(sys.argv) != 4):
    print sys.argv[0] + " /path/to/ssl.crt /path/to/ssl.key ProcessedMachineIdentifier"
    sys.exit(0)
  hash = hashlib.sha512()
  hash.update('plex')
  hash.update(sys.argv[3])
  passphrase = hash.hexdigest()

  with open(sys.argv[1], 'rb') as f:
    c = f.read()

  with open(sys.argv[2], 'rb') as f:
    k = f.read()

  key = load_privatekey(FILETYPE_PEM,k)
  cert = load_certificate(FILETYPE_PEM,c)
  p12 = PKCS12()
  p12.set_certificate(cert)
  p12.set_privatekey(key)
  open("certificate.p12", 'w' ).write( p12.export(passphrase) )

  print passphrase

if __name__ == '__main__':
  main()