# bigdecoder.py, by aderyn@gmail.com, 2009-03-01
#
# decoder for .BIG-format files utilized by Red Alert 3 and C&C: Zero Hours
# among others. .big is a trivial archival format. quite frankly, this is
# probably the simplest compound file format imaginable.
#
# this script is written for microsoft windows. it can probably be easily
# adapted for other platforms, but i haven't tried.
# 
# file structure:
# the file consists of a global header, an index of all the embedded
# files, and the actual file data.
#
# global header {
# header, charstring, 4 bytes - always BIG4 or something similiar
# total file size, unsigned integer, 4 bytes, little endian byte order
# number of embedded files, unsigned integer, 4 bytes, big endian byte order
# total size of index table in bytes, unsigned integer, 4 bytes, big endian byte order
# }, only occurs once
#
# index of files, follows directly after
# the global header:
# index entry {
# position of embedded file within BIG-file, unsigned integer, 4 bytes, big endian byte order
# size of embedded data, unsigned integer, 4 bytes, big endian byte order
# file name, cstring, ends with null byte
# }, repeats for each embedded file
#
# file data:
# raw file data at the positions specified in the index

import struct
import sys
import os
import os.path

# Define an empty class to emulate a c struct
# that can hold the data for each entry in the
# file index.
class entry:
	pass

if len(sys.argv) != 3:
	print "usage: python bigdecoder.py [file] [target]"
	exit()
	
print "BIG-file decoder by aderyn@gmail.com"

filePath = sys.argv[1]
targetDir = sys.argv[2]

if not os.path.exists(filePath):
	print "Requested file doesn't exist."
	exit()
	
if targetDir[-1] != "\\":
	targetDir += "\\"
	
print "Processing " + filePath

# open the file in binary read mode.
# without the b-flag the tell-method
# returns the wrong value.
file = open(filePath, "rb")

# read global header:

# this seems to vary. zero hour uses BIGF
header = file.read(4)
if header != "BIG4":
	print "Invalid file format."
	exit()

# this seems to be the only value encoded in
# little-endian order.
(size,) = struct.unpack("I", file.read(4))
print "size: %d" % (size,)

(entryCount,indexSize) = struct.unpack(">II", file.read(8))
print "entry count: %d" % (entryCount,)
print "index size: %d" % (indexSize,)

print

# read the index table:

# assume that the file contains the amount of 
# entries specified by the global header
entries = []
for j in xrange(0, entryCount):

	(entryPos,entrySize) = struct.unpack(">II", file.read(8))
	
	# the filename is stored as a cstring and
	# ends with a null byte. read until we reach
	# this byte.
	fileName = ""
	while True:
		n = file.read(1)
		if ord(n) == 0:
			break
		
		fileName += n
	
	e = entry()
	e.name = fileName
	e.position = entryPos
	e.size = entrySize
	
	entries.append(e)

# iterate through the index entries and
# copy the data into separate files.	
for i, e in enumerate(entries):
	print "opening %s (size: %d, position: %d)" % (e.name,e.size,e.position)
	print "file %d of %d" % (i+1, entryCount)
	
	# calculate the path where the file will be created
	# in order to ensure that the directories needed actually
	# exists
	fileTargetDir = targetDir + e.name[0:e.name.rfind("\\")] + "\\"
	fileName = e.name[e.name.rfind("\\")+1:]
	targetPath = fileTargetDir + fileName
	
	# create the directories if they don't exist.
	if not os.path.exists(fileTargetDir):
		os.makedirs(fileTargetDir)
		
	# skip files that already exist.
	if os.path.exists(targetPath):
		print "%s exists. Skipping." % (targetPath,)
		continue
	
	print "Opening %s for writing" % (targetPath,)
	targetFile = open(targetPath, "wb")
	
	print "Seeked to %d" % (e.position,)
	file.seek(e.position)
	
	print "Starting data transfer"
	for i in xrange(0, e.size):
		byte = file.read(1)
		targetFile.write(byte)
		
	print "Wrote %d bytes" % (e.size,)
	
	print "Done, closing file."
	targetFile.close()
	
	print
	
