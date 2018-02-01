#!/usr/bin/env python
#
# extracts and parse BackupKeyBag
#
# 2017.02.04 darell tan
#

from plist import *
import struct
import sys
from binascii import hexlify
from collections import OrderedDict

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO


def getKeybagFile(manifest_file):
	"""
	Retrieves the BackupKeyBag embedded within the Manifest.plist.
	"""
	with open(manifest_file, 'rb') as f:
		data = f.read()
		pl = Structure.from_bin(data) if data.startswith('bplist') \
			 else Structure.from_xml(data)

		assert 'Version' in pl

		return StringIO(pl['BackupKeyBag'].get_value())


class Keybag:
	def __init__(self, f):
		self.hdr = OrderedDict()
		self.keys = []

		self.f = f if hasattr(f, 'read') else open(f, 'rb')

		self._parse()

	def _parse(self):
		keys = []
		currKey = OrderedDict()
		while True:
			hdr = self.f.read(4+4)
			if hdr == '':
				break
			typ, sz = struct.unpack('>4sI', hdr)
			data = self.f.read(sz)
			if sz == 4:
				data, = struct.unpack('>I', data)

			# UUID usually first item of each entry
			if typ == 'UUID':
				if 'UUID' in currKey:
					keys.append(currKey)
				else:
					self.hdr = currKey
				currKey = OrderedDict()

			currKey[typ] = data

		if currKey:
			keys.append(currKey)

		self.keys = keys

	def dump(self):
		for k, v in self.hdr.iteritems():
			print k, v

		print '-' * 10

		def decode(typ, val):
			if typ == 'UUID':
				v = hexlify(val)
				return '%s...%s' % (v[:6], v[-4:])
			elif not isinstance(val, (int, long)):
				return hexlify(val)
			else:
				return repr(val)

		for key in self.keys:
			print ', '.join('%s: %s' % (k, decode(k, v)) \
					for k, v in key.iteritems())

	def __repr__(self):
		return repr(self.keys)

def main():
	stream = getKeybagFile(sys.argv[1])

	k = Keybag(stream)
	k.dump()

if __name__ == '__main__':
	main()
