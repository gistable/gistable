#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function

import os, sys
import struct as st
import time as tm

uint32 = '>I'
int32 = '>i'
uint16 = '>H'
int16 = '>h'
uint8 = 'B'
int8 = 'b'

#file header
file_version_number_fmt = uint32
app_version_number_fmt = uint32
idtag_length_fmt = uint16
length_length_fmt = uint16

#struct record header
tag_id_fmt = uint8 #=1byte file header idtag_length
length_fmt = uint16 #=2bytes file header length_length

#records const
recdomain = 0x01
recpath = 0x02
reccookie = 0x03

#msb flags
msb = 0x80
enddomain = (msb | 0x04)
endpath = (msb | 0x05)

#indent size
doind = 0
indent = 0


def readfmt(f, fmt):
	size = st.calcsize(fmt)
	data = f.read(size)
	if len(data) < size: raise EOFError('in readfmt, at pos:', f.tell())
	return st.unpack(fmt, data)[0]


def read(f, ln):
	data = f.read(ln)
	if len(data) < ln: raise EOFError('in read, at pos:', f.tell())
	return data


def getfhdr(f):
	fhdr = {}
	fhdr[1] = readfmt(f, file_version_number_fmt)
	fhdr[2] = readfmt(f, app_version_number_fmt)
	fhdr[3] = readfmt(f, idtag_length_fmt)
	fhdr[4] = readfmt(f, length_length_fmt)
	return fhdr


def getrecid(f):
	return readfmt(f, tag_id_fmt)


def getrechdr(f, hdr):
	global doind
	if (msb & hdr):
		if enddomain == hdr:
			doind = -1
			return True, 'end of domain record', 0
		elif endpath == hdr:
			return True, 'end of path record', 0
		else:
			return True, 'end of unknown record', 0,
	else:
		datalen = readfmt(f, length_fmt)
		if recdomain == hdr:
			doind = 1
			return False, 'domain record', datalen
		elif recpath == hdr:
			return False, 'path record', datalen
		elif reccookie == hdr:
			return False, 'cookie record', datalen
		else:
			return False, 'unknown record', datalen

def getddidname(did):
	flag = True if msb & did else False
	if 0x1e == did: name = 'name of the domain part'
	elif 0x1f == did: name = 'how cookies are filtered for this domain.'
	elif 0x21 == did: name = 'handling of cookies that have explicit paths'
	elif 0x25 == did: name = 'filter third party cookies mode'
	else: name = 'unknown domain data id'
	return flag, name


def getpdidname(did):
	flag = True if msb & did else False
	if 0x1d == did: name = 'the name of the path part'
	else: name = 'unknown path data id'
	return flag, name


def getcdidname(did):
	flag = True if msb & did else False
	if 0x10 == did: name = 'name of the cookie'
	elif 0x11 == did: name = 'value of the cookie'
	elif 0x12 == did: name = 'expiry'
	elif 0x13 == did: name = 'last used'
	elif 0x14 == did: name = 'comment/description of use'
	elif 0x15 == did: name = 'URL for comment/description of use'
	elif 0x16 == did: name = 'domain received with version=1 cookies'
	elif 0x17 == did: name = 'path received with version=1 cookies'
	elif 0x18 == did: name = 'port limitations received with version=1 cookies'
	elif 0x1A == did: name = 'version number of cookie'
	elif (0x19 | msb) == did: name = 'will only be sent to https servers'
	elif (0x1b | msb) == did: name = 'will only be sent to the server that sent it'
	elif (0x1c | msb) == did: name = 'reserved for delete protection: not yet implemented'
	elif (0x20 | msb) == did: name = 'will not be sent if the path is a prefix of the url'
	elif (0x22 | msb) == did: name = 'was set as the result of a password login form'
	elif (0x23 | msb) == did: name = 'was set as the result of a http authentication login'
	elif (0x24 | msb) == did: name = 'was set by a third party server'
	else: name = 'unknown cookie data id'
	return flag, name


def printt(*args):
	global indent
	if 0 > indent:
		print('indent:', indent)
	print('\t'*indent, *args, sep='')


def prsdomaindata(f, d):
	end = f.tell() + d[2]
	data = []
	while f.tell() < end:
		did = readfmt(f, tag_id_fmt)
		flag, dnam = getddidname(did)
		if not flag:
			dlen = readfmt(f, length_fmt)
			draw = read(f, dlen)
		else:
			dlen = 0
			draw = ''
		data.append((hex(did), dnam, dlen, draw))
	printt(data)
	return data


def prspathdata(f, d):
	end = f.tell() + d[2]
	data = []
	while f.tell() < end:
		did = readfmt(f, tag_id_fmt)
		flag, dnam = getpdidname(did)
		if not flag:
			dlen = readfmt(f, length_fmt)
			draw = read(f, dlen)
		else:
			dlen = 0
			draw = ''
		data.append((hex(did), dnam, dlen, draw))
	printt(data)
	return data


def frmtm(t):
	unp = st.unpack('>Q', t)[0]
	return tm.strftime('%Y-%m-%d %H:%M:%S', tm.localtime(unp))


def prscookiedata(f, d):
	end = f.tell() + d[2]
	data = []
	while f.tell() < end:
		did = readfmt(f, tag_id_fmt)
		flag, dnam = getcdidname(did)
		if not flag:
			dlen = readfmt(f, length_fmt)
			draw = read(f, dlen)
			if 0x12==did or 0x13==did:
				draw = frmtm(draw)
		else:
			dlen = 0
			draw = ''
		data.append((hex(did), dnam, dlen, draw))
	printt(data)
	return data


def process(f):
	global indent
	global doind
	f.seek(0, os.SEEK_END)
	fend = f.tell()
	f.seek(0, os.SEEK_SET)

	fhdr = getfhdr(f)
	print('file_version_number', fhdr[1])
	print('app_version_number', fhdr[2])
	print('idtag_length', fhdr[3])
	print('length_length', fhdr[4])

	if (fhdr[3] != 1) and (fhdr[4] != 2):
		printt('Not compatible')
		return
	while(f.tell() < fend):
		try:
			rhdr = getrecid(f)
			rdat = getrechdr(f, rhdr)
			if True == rdat[0]:
				indent += doind
				doind = 0
				printt(rdat[1])
			elif False == rdat[0]:
				printt(rdat[1])
				indent += doind
				doind = 0
				if rhdr == recdomain:
					prsdomaindata(f, rdat)
				elif rhdr == recpath:
					prspathdata(f, rdat)
				elif rhdr == reccookie:
					prscookiedata(f, rdat)
				else:
					printt('parse unknown record')
		except EOFError as e:
			printt('EOFError', e)
			input()
			break


def main():
	if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
		file = open(sys.argv[1], 'rb')
		process(file)
		file.close()


if __name__ == '__main__':
	try:
		main()
	except:
		import traceback
		print('Unhandled exception:\n')
		traceback.print_exc()
		input('\nPress any key...')
