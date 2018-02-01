#!/usr/bin/python

# The Samsung trailer format is based on the implementation from ExifTool
# http://www.sno.phy.queensu.ca/~phil/exiftool/

import mmap
import struct
import os
import sys

if (len(sys.argv) < 2) or (len(sys.argv) > 3):
	print("Usage: fix_eoi.py <filename> [dump]")
	exit()

file = sys.argv[1]

if len(sys.argv) < 3:
	dump = 0
elif sys.argv[2] == "dump":
	dump = 1
else:
	print("Invalid argument")
	print("Usage: fix_eoi.py <filename> [dump]")
	exit()

(file_name, file_ext) = os.path.splitext(file)

with open(file, 'rb') as fh:
	m = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
	b = bytearray(m)
	
	trailer_tail = b[-4:]
	
	if trailer_tail != 'SEFT':
		print("No valid Samsung trailer found")
		exit()
	else:
		print("Found SEFT")
	
	length = struct.unpack_from("<I",b[-8:-4])[0]	
	trailer = b[-(8+length):]
	
	endPos = len(b)
	dirPos = endPos-(8+length)
	
	if trailer[0:4] != 'SEFH':
		print("No valid Samsung trailer found")
		exit()
	else:
		print("Found SEFH")
	
	version = struct.unpack_from("<I",trailer[4:8])[0]
	if version != 101:
		print("Unknown Samsung trailer version")
		exit()
	
	count = struct.unpack_from("<I",trailer[8:12])[0]
	
	firstBlock = 0
	is_pano = 0
	
	for index in range(0, count):
		entry = 12 + 12 * index;
		
		type = struct.unpack_from("<H",trailer[entry+2:entry+4])[0]
		noff = struct.unpack_from("<I",trailer[entry+4:entry+8])[0]
		size = struct.unpack_from("<I",trailer[entry+8:entry+12])[0]
		
		if firstBlock < noff:
			firstBlock = noff
		
		entryPos = dirPos - noff
		entryLen = size
		
		data = b[entryPos:entryPos+entryLen]
		
		# Validate as the type has to match the SEFH/SEFT entry type
		entry_type = struct.unpack_from("<H",data[2:4])[0]
		if type != entry_type:
			print("Missmatch detected. Aborting!")
			exit()
			
		entry_offset = struct.unpack_from("<I",data[4:8])[0]
		entry_name = data[8:8+entry_offset].decode("utf-8") 
		
		if entry_name == "Panorama_Shot_Info":
			is_pano = 1
		
		entry_data = data[8+entry_offset:]
		
		if dump:
			print("Dumping: %s" % entry_name)
			with open(file_name + '_' + entry_name, 'wb') as f:
				f.write(entry_data)

	if not is_pano:
		print "No Panorama info found"
		exit()
	
	dataPos = dirPos - firstBlock
	dirLen = endPos - dataPos
	
	eoi = struct.unpack_from(">H",b[dataPos-2:dataPos])[0]
	if eoi == 0xffd9:
		print("Found EOI")
		exit()
	else:
		print("Inserting EOI")
		with open(file_name + '_pano' + file_ext, 'wb') as f:
				f.write(b[0:dataPos])
				f.write(bytearray(b'\xff\xd9'))
				f.write(b[dataPos:])
	