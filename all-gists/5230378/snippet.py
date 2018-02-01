import os
import sys

def CleanFile(fileA, fileB):
	f = open(fileA, "rb")
	w = open(fileB, "wb")
	try:
		byte = f.read(1)
		while byte != "":
			if ord(byte) == 10:
				w.write(byte)
			if ord(byte) >= 32 and ord(byte) <= 126:
				w.write(byte)
			byte = f.read(1)
	finally:
		f.close()
		w.close()

if len(sys.argv) == 3:
        CleanFile(sys.argv[1], sys.argv[2])
else:
        print "asciiclean.py [input file] [output file]"