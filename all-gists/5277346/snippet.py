#!/usr/bin/env python3

'''
Layout of buka manga archives
  Whole archive
    | b"buka" | unknown (16 bytes) | manga title (c string) | entry table | file 1 | file 2 | ...

  Entry table
    | table size (uint32) | entry 1 | entry 2 | ... |

  Entry
    | offset (uint32) | size (uint32) | name (c string) |

  Note
    c string: null terminated, encoded in utf8.
    unit32: 32 bit, unsigned, little endian.
    table size contains the size of itself.
'''

import sys, os, struct


def readuint32(src):
	buf = src.read(4)
	return struct.unpack('<I', buf)[0]

def readcstring(src):
	buf = b""
	while True:
		ch = src.read(1)
		if ch[0] == 0:
			return buf.decode('utf8'), len(buf) + 1
		buf += ch

def readtable(src):
	table = []
	tsize = readuint32(src)
	total = 4
	while total < tsize:
		offset = readuint32(src)
		size = readuint32(src)
		name, n = readcstring(src)
		if name not in ["index2.dat", "chaporder.dat", "logo"]:
			table.append((offset, size, name))
		total += n + 8
	return table

def copysection(dst, src, offset, size):
	src.seek(offset)
	dst.write(src.read(size))

def fmtsize(size):
	for i in "kmgt":
		size /= 1024
		if size < 1024:
			return "%.2f"%size + i

def extract(srcfile):
	dstdir = os.path.join(os.path.dirname(srcfile), os.path.splitext(os.path.basename(srcfile))[0])
	if not os.path.exists(dstdir):
		os.mkdir(dstdir)

	with open(srcfile, 'rb') as src:
		if src.read(4) != b'buka':
			print("%s: not a buka manga archive" % srcfile)
			return
		src.seek(20)
		title, _ = readcstring(src)
		table = readtable(src)

		print("extract %s (%s) to %s/" % (srcfile, title, dstdir))
		for offset, size, name in table:
			dstfile = os.path.join(dstdir, name)
			with open(dstfile, 'wb') as dst:
				copysection(dst, src, offset, size)
				print("  %s (%s)" % (name, fmtsize(size)))

for srcfile in sys.argv[1:]:
	extract(srcfile)
