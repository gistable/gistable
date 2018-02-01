#!/usr/bin/env python

from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor
from binascii import hexlify

K = '0123456789abcdef'
cipher = AES.new(K, AES.MODE_ECB)

# Original Message
M1 = K
M2 = K
Cm0 = cipher.encrypt('\0' * AES.block_size)
Cm1 = cipher.encrypt(strxor(Cm0,M1))
Tm = Cm2 = cipher.encrypt(strxor(Cm1,M2))

N1 = 'iheiowehfiowehfw'

# Inject second message after the first message
Cx0 = cipher.encrypt('\0' * AES.block_size)
Cx1 = cipher.encrypt(strxor(Cx0,M1))
Cx2 = cipher.encrypt(strxor(Cx1,N1))
# X needs to *encrypt* to the same value as Cm1
X = strxor(cipher.decrypt(Cx1),Cx2)
Cx3 = cipher.encrypt(strxor(Cx2,X))
Tx = Cx4 = cipher.encrypt(strxor(Cx3,M2))

print "Tm = '%s'" % hexlify(Tm)
print "Tx = '%s'" % hexlify(Tx)
