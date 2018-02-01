#!/usr/bin/env python

# with help and inspiration from
#  * ASN1_generate_nconf(3) (specifically the SubjectPublicKeyInfo structure)
#  * http://www.sysmic.org/dotclear/index.php?post/2010/03/24/Convert-keys-betweens-GnuPG%2C-OpenSsh-and-OpenSSL
#  * http://blog.oddbit.com/2011/05/converting-openssh-public-keys.html

import sys
import base64
import struct
from pyasn1.type import univ
from pyasn1.codec.der import encoder as der_encoder, decoder as der_decoder

if len(sys.argv) != 2:
    sys.stderr.write("Usage: %s <public key file>\n" % sys.argv[0])
    sys.exit(1)

keyfields = open(sys.argv[1]).read().split(None)
if len(keyfields) < 3:
    # there might not be a comment, so pad it
    keyfields.append("")
keytype, keydata, keycomment = keyfields

if keytype != 'ssh-rsa':
    sys.stderr.write("%s: key type does not appear to be ssh-rsa\n")
    sys.exit(1)

keydata = base64.b64decode(keydata)

parts = []
while keydata:
   # read the length of the data
    dlen = struct.unpack('>I', keydata[:4])[0]

    # read in <length> bytes
    data, keydata = keydata[4:dlen+4], keydata[4+dlen:]

    parts.append(data)

e_val = eval('0x' + ''.join(['%02X' % struct.unpack('B', x)[0] for x in parts[1]]))
n_val = eval('0x' + ''.join(['%02X' % struct.unpack('B', x)[0] for x in parts[2]]))

bitstring = univ.Sequence()
bitstring.setComponentByPosition(0, univ.Integer(n_val))
bitstring.setComponentByPosition(1, univ.Integer(e_val))

bitstring = der_encoder.encode(bitstring)

bitstring = ''.join([('00000000'+bin(ord(x))[2:])[-8:] for x in list(bitstring)])

bitstring = univ.BitString("'%s'B" % bitstring)

pubkeyid = univ.Sequence()
pubkeyid.setComponentByPosition(0, univ.ObjectIdentifier('1.2.840.113549.1.1.1')) # == OID for rsaEncryption
pubkeyid.setComponentByPosition(1, univ.Null(''))

pubkey_seq = univ.Sequence()
pubkey_seq.setComponentByPosition(0, pubkeyid)
pubkey_seq.setComponentByPosition(1, bitstring)

print "-----BEGIN PUBLIC KEY-----"
if keycomment:
    print "X-Comment: " + keycomment
    print
base64.MAXBINSIZE = (64//4)*3 # this actually doesn't matter, but it helped with comparing to openssl's output
print base64.encodestring(der_encoder.encode(pubkey_seq)),
print '-----END PUBLIC KEY-----'
