#!/usr/bin/python

# Decoder for the ExportedSharedSecret values stored in .networkConnect files
# Tested with .networkConnect files created in Mac OS X 10.10
#
# Author: Martin Rakhmanov, http://jimmers.info
#
# Example invocation and output:
#
# python vpn_shared_secret_decoder.py TLthF+e88vwmAYhK
# Shared Secret: 12345

import sys
import base64

if len(sys.argv) != 2:
    print("Provide ExportedSharedSecret value from .networkConnect file")
    sys.exit(1)

cryptotext = base64.b64decode(sys.argv[1])

decryption_key = [0x7d, 0x89, 0x52, 0x23, 0xd2, 0xbc, 0xdd, 0xea, 0xa3, 0xb9, 0x1f]

i = 0
cleartext = ""

for ch in cryptotext:
    b = ord(ch) ^ decryption_key[i]
    if b == 0x00:
        break
    cleartext += chr(b)
    i += 1
    i = i % len(decryption_key)

print("Shared Secret: %s" %(cleartext))
