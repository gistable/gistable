#!/usr/bin/python

'''
Python implementation of passcode hashing algorithm used on the Samsung Galaxy S4 GT-I9505 4.2.2
Correct PIN for hash and salt below is 1234.

Get 40-character hash value in ascii hex format from file /data/system/password.key on the phone

Get salt in signed numeric format by doing sqlite3 query SELECT value FROM locksettings WHERE name = 'lockscreen.password_salt' on /data/system/locksettings.db

by @hubert3 2014-01-23
'''

import sys
from hashlib import sha1
from binascii import unhexlify

def get_salt(salt):
        int_salt = int(salt)   
        int_salt = (int_salt & 0xffffffffffffffff)
        salt = hex(int(int_salt)).lstrip("0x")
        salt = salt.rstrip('L')
        return salt

samsung_hash = unhexlify('867B4B7F6C7E5CCC50A1BD183D8C3E5801F20344'.lower())
salt = get_salt(-3343618892075477414)

for pin in map('{:04}'.format,range(0,10000)):
	print 'Hashing PIN %s' % pin
 	digest = sha1('0'+pin+salt).digest() # binary digest, not ascii hex
	for i in map(str,range(1,1024)): # Samsung uses 1024 SHA-1 iterations
		digest = sha1(digest+i+pin+salt).digest()
	if digest == samsung_hash:
		print 'FOUND PIN %s' % pin
		sys.exit(0)
print 'PIN not found'

