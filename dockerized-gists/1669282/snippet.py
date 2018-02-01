import sys
import os
from struct import unpack

def splitMPO( mpof ):
	filename = mpof.name
	#print "MPO input: {}".format(filename)
	#check SOI
	soi = mpof.read(2)
	if soi != "\xff\xd8" :
		print "{} is not a MPO file.(Bad SOI)".format(filename)
		return
	
	#read APP1
	app1 = mpof.read(10)
	if app1[4:8] != "Exif" :
		print "{} is not a MPO file.(\"Exif\" not found in APP1)".format(filename)
		return
	
	app1len = unpack(">H", app1[2:4])[0]
	#print "APP1 length :{}".format(app1len)
	mpof.seek(app1len - 8, os.SEEK_CUR) # data length is not include tag length (2byte).
	
	#read App2
	while True:
		app2 = mpof.read(8)
		if app2[:2] != "\xff\xe2" :
			print "{} is not a MPO file.(\"MPF\" not found in APP2)".format(filename)
			return
		
		app2len = unpack(">H", app2[2:4])[0]
		#print "APP2 length :{}".format(app2len)
		
		if app2[4:7] != "MPF" :
			#find next APP2
			mpof.seek(app2len - 6, os.SEEK_CUR)
		else:
			offsetbase = mpof.tell()
			mpfendian = mpof.read(4)
			if mpfendian == "\x49\x49\x2a\x00":
				endianpref = "<" #little endian
			else:
				endianpref = ">" #big endian
			ifdoffset = unpack( endianpref + "L", mpof.read(4) )[0]
			#print "IFD Offset: {}".format(ifdoffset)
			mpof.seek( ifdoffset - 8, os.SEEK_CUR )
			break
	
	#print "MPF endian type: {0}, offset base: {1}, tell: {2}".format( endianpref, offsetbase, mpof.tell() )
	
	#read MPIndex
	mpidcount = unpack( endianpref + "H", mpof.read(2) )[0]
	#print "MPIndex has {} datas".format(mpidcount)
	for i in range(mpidcount):
		mpiddata = mpof.read(12)
		mpidtag = unpack( endianpref + "H", mpiddata[:2] )[0]
		#print "tag[{0}]: {1:x}".format(i, mpidtag)
		#if mpidtag == 0xb000:
		#	print "{0:x} format version: {1}".format(mpidtag, mpiddata[8:])
		#el
		if mpidtag == 0xb001:
			imagecount = unpack( endianpref + "L", mpiddata[8:] )[0]
			#print "{0:x} image count: {1}".format(mpidtag, imagecount)
		elif mpidtag == 0xb002:
			entryoffset = unpack( endianpref + "L", mpiddata[8:] )[0]
			#print "{0:x} entry offset: {1}".format(mpidtag, entryoffset)
	
	mpof.seek( offsetbase + entryoffset, os.SEEK_SET )
	#print mpof.tell()
	imageinfo = []
	for i in range(imagecount):
		mpentrydata = mpof.read(16)
		imageinfo.append( unpack( endianpref + "LLL", mpentrydata[:12] ) )#[flags(L)][size(L)][offset(L)]
		#print "image[{}] size: {}, offset:{}({})".format(i, imageinfo[i][1], imageinfo[i][2], imageinfo[i][2] + offsetbase)
	
	#split images
	for i, imginfo in enumerate(imageinfo):
		try:
			#seek
			if imginfo[2] > 0:
				mpof.seek( offsetbase + imginfo[2], os.SEEK_SET )
			else:
				mpof.seek( 0, os.SEEK_SET )
			#output file
			outname = "{}_mp{}.jpg".format(filename[:-4], i)
			outf = open( outname, "wb" )
		except IOError as inst:
			print inst
		else:
			outf.write( mpof.read(imginfo[1]) )
			outf.close()
			print "output {} ({} bytes)".format(outname, imginfo[1])

if len(sys.argv) <= 1:
	print "split MPO files to JPEG images."
	print "usage {} mpofile1 mpofile2 ...".format(sys.argv[0])
	exit()

for i,a in enumerate(sys.argv[1:]):
	print "input[{0}] :{1}".format(i, a)
	try:
		mpof = open(a, "rb")
	except IOError as inst:
		print inst
	else:
		splitMPO(mpof)
		mpof.close()
	
