#! /usr/bin/env python2.7
#
# Author: Pat Litke (C) 2014
#
# This code is released under the WTFPL V2 http://www.wtfpl.net/
#
# License:
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
# TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
#
# Description:
# Quick and dirty module to read a binary file, look at the DOS header for the PE offset
#   Seek to the PE offset, read the third DWORD in, unpack it, and return either EPOCH or GMTIMEs
#
#	NOTE: DON'T USE THIS IN PRODUCTION. This was a demo/learning experience. It's published here in hopes someone will find it  useful
#
# Returns 1 if the file doesn't havea a DOS header
# Returns 2 if file couldn't be read
# Returns the data in epoch or formatted otherwise

from struct import unpack
from binascii import hexlify
from time import gmtime, strftime

def getEpoch(filePath, epoch = True):
	
	# Open the file in Binary mode
	try:
		handle = open(filePath, 'rb')
		if hexlify(handle.read(2)) != hexlify(u'MZ'):
			handle.close()
			return
	except:
		return

	try:
		# Get PE offset (@60, DWORD) from DOS header
		#	It's little-endian so we have to flip it
		#	We also need the HEX representation which is an INT value
		handle.seek(60, 0)
		offset = handle.read(4)
		offset = hexlify(offset[::-1])

		# This was added in due to an issue with offset being set to '' on rare occasions (see comments below)
		if offset == '':
			handle.close()
			return

		#	ValueError: invalid literal for int() with base 16: ''
		#	https://stackoverflow.com/questions/11826054/valueerror-invalid-literal-for-int-with-base-16-x0e-xa3-python
		#	https://stackoverflow.com/questions/20375706/valueerror-invalid-literal-for-int-with-base-10-python
		#		This indicates that for some reason, 'offset' from above is being set as '' and thus can't be converted to a base 16 int
		offset = int(offset, 16)

		# Seek to PE header and read second DWORD
		handle.seek(offset+8, 0)
		dword = handle.read(4)
		handle.close()

		# Attempt to unpack
		#	This try was added in because some files pass the above check, but still cause the unpack to puke
		#	eg: struct.error: unpack requires a string argument of length 4
	
		t = unpack(">L", dword[::-1])[0]
	except:
		return

	if epoch:
		return t
	else:
		return strftime('%Y-%m-%d %H:%M:%S', gmtime(float(t)))



def getUTC(filePath):
	return getEpoch(filepath, False)

def getBoth(filePath):
	return [getEpoch(filepath), getEpoch(filepath, False)]