import struct
import math
import os
import sys
from PIL import Image
from subprocess import call

if sys.version > '3':
	buffer = memoryview

def getWord(b, k, n=4):
	return sum(list(map(lambda c: b[k+c]<<(c*8),range(n))))

totalVcount=1
currentVcount=0

totalNcount=1
currentNcount=0
hasNormals=False

totalTCcount=1
currentTCcount=0

def parseVertices(b, o, s, f):
	global hasNormals
	global currentVcount, currentNcount, currentTCcount
	if f==0x0C:
		#for 3-word vertex descriptors
		for i in range(int(s/f)):
			arr=[struct.unpack('f',buffer(srcdata[(o+k*4):(o+(k+1)*4)]))[0] for k in range(3)]
			print("v  "+str(arr[0])+" "+str(arr[1])+"   "+str(arr[2]))
			currentVcount=currentVcount+1
			o=o+f
	if f==0x14:
		#for 5-word vertex descriptors
		for i in range(int(s/f)):
			arr=[struct.unpack('f',buffer(srcdata[(o+k*4):(o+(k+1)*4)]))[0] for k in range(5)]
			print("v  "+str(arr[0])+" "+str(arr[1])+"   "+str(arr[2]))
			print("vt  "+str(arr[3])+" "+str(arr[4]))
			currentVcount=currentVcount+1
			currentTCcount=currentTCcount+1
			o=o+f
	elif f==0x18:
		#for 6-word vertex descriptors
		for i in range(int(s/f)):
			arr=[struct.unpack('f',buffer(srcdata[(o+k*4):(o+(k+1)*4)]))[0] for k in range(6)]
			print("v  "+str(arr[0])+" "+str(arr[1])+"   "+str(arr[2]))
			print("vt  "+str(arr[4])+" "+str(arr[5]))
			currentVcount=currentVcount+1
			currentTCcount=currentTCcount+1
			o=o+f
	elif f==0x20 or f==0x24 or f==0x28:
		#for 8-word vertex descriptors
		#for 9-word vertex descriptors
		#for 10-word vertex descriptors
		for i in range(int(s/f)):
			arr=[struct.unpack('f',buffer(srcdata[(o+k*4):(o+(k+1)*4)]))[0] for k in range(8)]
			print("v  "+str(arr[0])+" "+str(arr[1])+"   "+str(arr[2]))
			print("vn  "+str(arr[3])+" "+str(arr[4])+"   "+str(arr[5]))
			print("vt  "+str(arr[6])+" "+str(arr[7]))
			hasNormals=True
			currentVcount=currentVcount+1
			currentNcount=currentNcount+1
			currentTCcount=currentTCcount+1
			o=o+f

def parseFaces(b, o, s, f):
	global hasNormals
	global totalVcount, totalNcount, totalTCcount
	global currentVcount, currentNcount, currentTCcount

	if f==1:
		#for u8 face descriptors
		for i in range(int(s/(3))):
			arr=[struct.unpack('B',buffer(srcdata[(o+k):(o+(k+1))]))[0] for k in range(8)]
			if hasNormals:
				print("f "+str(arr[0]+totalVcount)+"/"+str(arr[0]+totalTCcount)+"/"+str(arr[0]+totalNcount)+" "+
					str(arr[1]+totalVcount)+"/"+str(arr[1]+totalTCcount)+"/"+str(arr[1]+totalNcount)+" "+
					str(arr[2]+totalVcount)+"/"+str(arr[2]+totalTCcount)+"/"+str(arr[2]+totalNcount))
			else:
				print("f "+str(arr[0]+totalVcount)+" "+str(arr[1]+totalVcount)+" "+str(arr[2]+totalVcount))
			o=o+3
	elif f==3:
		#for u16 face descriptors
		for i in range(int(s/(3*2))):
			arr=[struct.unpack('H',buffer(srcdata[(o+k*2):(o+(k+1)*2)]))[0] for k in range(8)]
			if hasNormals:
				print("f "+str(arr[0]+totalVcount)+"/"+str(arr[0]+totalTCcount)+"/"+str(arr[0]+totalNcount)+" "+
					str(arr[1]+totalVcount)+"/"+str(arr[1]+totalTCcount)+"/"+str(arr[1]+totalNcount)+" "+
					str(arr[2]+totalVcount)+"/"+str(arr[2]+totalTCcount)+"/"+str(arr[2]+totalNcount))
			else:
				print("f "+str(arr[0]+totalVcount)+" "+str(arr[1]+totalVcount)+" "+str(arr[2]+totalVcount))
			o=o+6

	totalVcount=totalVcount+currentVcount
	totalNcount=totalNcount+currentNcount
	totalTCcount=totalTCcount+currentTCcount
	currentVcount=0
	currentNcount=0
	currentTCcount=0

def parseSOBJ(b, o):
	global hasNormals
	dataStructOffset=getWord(b, o+0x44)
	
	print("# SOBJ "+hex(o))
	hasNormals=False
	if(dataStructOffset!=0):
		dataStructOffset=o+dataStructOffset

		faceDataFormat=getWord(b,dataStructOffset+0x18,1)
		faceDataSize=getWord(b,dataStructOffset+0x20)
		faceDataOffset=dataStructOffset+0x24+getWord(b,dataStructOffset+0x24)

		vertexDataFormat=getWord(b,dataStructOffset+0x68,1)
		vertexDataSize=getWord(b,dataStructOffset+0x58)
		vertexDataOffset=dataStructOffset+0x5C+getWord(b,dataStructOffset+0x5C)

		print("# vertex format "+hex(vertexDataFormat))
		parseVertices(b, vertexDataOffset, vertexDataSize, vertexDataFormat)

		print("g SOBJ_"+hex(o))

		parseFaces(b, faceDataOffset, faceDataSize, faceDataFormat)

#returns RGBA tuple (with added pixel size)
#format ID only confirmed for 0, 4, 5 and 7 !
def parsePixel(b, o, f):
	if f==0:
		#RGBA8
		pixel=getWord(b, o, 1)
		return ((getWord(b, o+3, 1), getWord(b, o+2, 1), getWord(b, o+1, 1), getWord(b, o, 1)), 4)
	elif f==1:
		#RGB8
		pixel=getWord(b, o, 1)
		return ((getWord(b, o, 1), getWord(b, o+1, 1), getWord(b, o+2, 1), 255), 3)
	elif f==2:
		#RGBA5551
		pixel=getWord(b, o, 2)
		return ((((pixel>>11)&0x1F)*8, ((pixel>>6)&0x1F)*8, ((pixel>>1)&0x1F)*8, (255 if pixel&0x1==1 else 0)), 2)
	elif f==3:
		#RGB565
		pixel=getWord(b, o, 2)
		return ((((pixel>>11)&0x1F)*8, ((pixel>>5)&0x3F)*4, ((pixel)&0x1F)*8, 255), 2)
	elif f==4:
		#RGBA4
		pixel=getWord(b, o, 2)
		return ((((pixel>>12)&0xF)*16, ((pixel>>8)&0xF)*16, ((pixel>>4)&0xF)*16, (pixel&0xF)*16), 2)
	elif f==5:
		#LA8
		pixel=getWord(b, o+1, 1)
		return ((pixel, pixel, pixel, getWord(b, o, 1)),2)
	elif f==7:
		#L8
		pixel=getWord(b, o, 1)
		return ((pixel, pixel, pixel, 255),1)
	# elif f==0xA:
	# 	#?
	# 	return ((0,0,0,0), 1)
	# elif f==0xC:
	# 	#?
	# 	return ((0,0,0,0), 1)
	elif f==0xD:
		#A4 ?
		return ((0,0,0,0), 1)
	else:
		print("# unknown format : "+hex(f))
		return ((0,0,0,0), 1)


tileOrder=[0,1,8,9,2,3,10,11,16,17,24,25,18,19,26,27,4,5,12,13,6,7,14,15,20,21,28,29,22,23,30,31,32,33,40,41,34,35,42,43,48,49,56,57,50,51,58,59,36,37,44,45,38,39,46,47,52,53,60,61,54,55,62,63]
def parseTile(im, b, o, f, x, y):
	global tileOrder
	for k in range(8*8):
		i=tileOrder[k]%8
		j=int((tileOrder[k]-i)/8)
		pixel=parsePixel(b,o,f)
		im.putpixel((x+i,y+j), pixel[0])
		o=o+pixel[1]
	return o

def parseTexture(b, o, s, w, h, f):
	im = Image.new("RGB", (w,h))

	dstname="tex_"+hex(o)+".png"

	if f==0xB or f==0xC:
		#ETC1; used external etc program (see https://gist.github.com/smealum/8897237 )
		open("tmp_etc","wb").write(b[o:(o+s)])
		#not super clean
		call(["etc.exe", "tmp_etc", str(w), str(h)])
		imgData=bytearray(open("tmp_etc.data","rb").read())
		for j in range(0,h):
			for i in range(0,w):
				k=(i+j*w)*4
				im.putpixel((i,j), (imgData[k],imgData[k+1],imgData[k+2],imgData[k+3]))
	else:
		for j in range(0,h,8):
			for i in range(0,w,8):
				o=parseTile(im, b, o, f, i, j)

	im.save(dstname)

def parseTXOB(b, o):
	textureDataWidth=getWord(b,o+0x18)
	textureDataHeight=getWord(b,o+0x14)
	if textureDataWidth!=0 and textureDataHeight!=0:
		textureDataFormat=getWord(b,o+0x30,1)
		textureDataSize=getWord(b,o+0x40)
		textureDataOffset=o+0x44+getWord(b,o+0x44)
		#o=o+0x20
		#print(hex(textureDataOffset)+" : "+hex(getWord(b,o))+" "+hex(getWord(b,o+4*1))+" "+hex(getWord(b,o+4*2))+" "+hex(getWord(b,o+4*3))+" "+hex(getWord(b,o+4*4))+" "+hex(getWord(b,o+4*5))+" "+hex(getWord(b,o+4*6))+" "+hex(getWord(b,o+4*7))+" "+
		#	hex(getWord(b,o+4*8))+" "+hex(getWord(b,o+4*9))+" "+hex(getWord(b,o+4*10))+" ")
		parseTexture(b, textureDataOffset, textureDataSize, textureDataWidth, textureDataHeight, textureDataFormat)


srcfn=sys.argv[1]

srcdata=bytearray(open(srcfn, 'rb').read())

for i in range(int(len(srcdata)/4)):
	#scan for SOBJ
	if getWord(srcdata, i*4)==0x4A424F53:
		parseSOBJ(srcdata,i*4)
	# #scan for TXOB
	if getWord(srcdata, i*4)==0x424F5854:
		parseTXOB(srcdata,i*4)

