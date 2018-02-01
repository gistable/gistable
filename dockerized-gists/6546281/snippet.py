
import struct

huffmanSegment = '\xFF\xC4\x01\xA2\x00\x00\x01\x05\x01\x01\x01\x01'\
	'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02'\
	'\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x01\x00\x03'\
	'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00'\
	'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'\
	'\x0A\x0B\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05'\
	'\x05\x04\x04\x00\x00\x01\x7D\x01\x02\x03\x00\x04'\
	'\x11\x05\x12\x21\x31\x41\x06\x13\x51\x61\x07\x22'\
	'\x71\x14\x32\x81\x91\xA1\x08\x23\x42\xB1\xC1\x15'\
	'\x52\xD1\xF0\x24\x33\x62\x72\x82\x09\x0A\x16\x17'\
	'\x18\x19\x1A\x25\x26\x27\x28\x29\x2A\x34\x35\x36'\
	'\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A'\
	'\x53\x54\x55\x56\x57\x58\x59\x5A\x63\x64\x65\x66'\
	'\x67\x68\x69\x6A\x73\x74\x75\x76\x77\x78\x79\x7A'\
	'\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94\x95'\
	'\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8'\
	'\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2'\
	'\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5'\
	'\xD6\xD7\xD8\xD9\xDA\xE1\xE2\xE3\xE4\xE5\xE6\xE7'\
	'\xE8\xE9\xEA\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9'\
	'\xFA\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05'\
	'\x04\x04\x00\x01\x02\x77\x00\x01\x02\x03\x11\x04'\
	'\x05\x21\x31\x06\x12\x41\x51\x07\x61\x71\x13\x22'\
	'\x32\x81\x08\x14\x42\x91\xA1\xB1\xC1\x09\x23\x33'\
	'\x52\xF0\x15\x62\x72\xD1\x0A\x16\x24\x34\xE1\x25'\
	'\xF1\x17\x18\x19\x1A\x26\x27\x28\x29\x2A\x35\x36'\
	'\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A'\
	'\x53\x54\x55\x56\x57\x58\x59\x5A\x63\x64\x65\x66'\
	'\x67\x68\x69\x6A\x73\x74\x75\x76\x77\x78\x79\x7A'\
	'\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94'\
	'\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7'\
	'\xA8\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA'\
	'\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4'\
	'\xD5\xD6\xD7\xD8\xD9\xDA\xE2\xE3\xE4\xE5\xE6\xE7'\
	'\xE8\xE9\xEA\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA'

class ParseJpeg(object):
	def __init__(self):
		pass

	def Open(self, fiHandle, verbose = 0):	
		#This function steps through the JPEG structure but
		#does nothing useful. It might be a useful basis for
		#extension.
	
		data = fiHandle.read()
		parsing = True
		frameStartPos = 0
		while parsing:
			#Check if we should stop
			if frameStartPos >= len(data):
				parsing = False
				continue

			#Read the next segment
			twoBytes, frameStartPos, frameEndPos = self.ReadFrame(data, frameStartPos)
			if verbose:
				print map(hex, twoBytes), frameStartPos, frameEndPos

			#Move cursor
			frameStartPos = frameEndPos

	def InsertHuffmanTable(self, fiHandle, outHandle, verbose = 0):
		#This converts an MJPEG frame into a standard JPEG binary
		#MJPEG images omit the huffman table if the standard table
		#is used. If it is missing, this function adds the table
		#into the file structure.

		data = fiHandle.read()
		parsing = True
		frameStartPos = 0
		huffFound = False
		while parsing:
			#Check if we should stop
			if frameStartPos >= len(data):
				parsing = False
				continue

			#Read the next segment
			twoBytes, frameStartPos, frameEndPos = self.ReadFrame(data, frameStartPos)
			if verbose:
				print map(hex, twoBytes), frameStartPos, frameEndPos

			#Stop if there is a serious error
			if frameStartPos is None:
				parsing = False
				continue

			#Check if this segment is the compressed data
			if twoBytes[0] == 0xff and twoBytes[1] == 0xda and not huffFound:
				outHandle.write(huffmanSegment)

			#Check the type of frame
			if twoBytes[0] == 0xff and twoBytes[1] == 0xc4:
				huffFound = True

			#Write current structure to output
			outHandle.write(data[frameStartPos:frameEndPos])

			#Move cursor
			frameStartPos = frameEndPos		

	def ReadFrame(self, data, offset):
		#Based on http://www.gdcl.co.uk/2013/05/02/Motion-JPEG.html
		#and https://en.wikipedia.org/wiki/JPEG

		cursor = offset
		#Check frame start
		frameStartPos = offset
		twoBytes = struct.unpack_from("BB", data, cursor)
		if twoBytes[0] != 0xff:
			print "Error: found header", map(hex,twoBytes),"at position",cursor
			return twoBytes, None, None

		#print map(hex, twoBytes)
		cursor += 2
		
		#Handle padding
		paddingByte = twoBytes[0] == 0xff and twoBytes[1] == 0xff
		if paddingByte: return twoBytes, frameStartPos, cursor

		#Structure markers with 2 byte length
		markHeader = twoBytes[0] == 0xff and twoBytes[1] >= 0xd0 and twoBytes[1] <= 0xd9
		if markHeader: return twoBytes, frameStartPos, cursor

		#Determine length of compressed (entropy) data
		compressedDataStart = twoBytes[0] == 0xff and twoBytes[1] == 0xda
		if compressedDataStart:
			sosLength = struct.unpack_from(">H", data, cursor)[0]
			cursor += sosLength

			#Seek through frame
			run = True
			entropyData = ""
			while run:
				byteEnc = data[cursor]
				byte = struct.unpack_from("B", data, cursor)[0]
				cursor += 1
			
				if byte == 0xff:
					byte2 = struct.unpack_from("B", data, cursor)[0]
					cursor += 1
					if byte2 != 0x00:
						if byte2 >= 0xd0 and byte2 <= 0xd8:
							#Found restart structure
							#print hex(byte), hex(byte2)
							pass
						else:
							#End of frame
							run = 0
							cursor -= 2
					else:
						#Add escaped 0xff value in entropy data
						entropyData += byteEnc
				else:
					entropyData += byteEnc

			return twoBytes, frameStartPos, cursor

		#More cursor for all other segment types
		segLength = struct.unpack_from(">H", data, cursor)[0]
		#print "segLength", segLength
		cursor += segLength
		
		return twoBytes, frameStartPos, cursor

if __name__ == "__main__":

	pj = ParseJpeg()
	pj.InsertHuffmanTable(open("test.mjpeg","rb"), open("test2.jpeg","wb"), verbose = 1)
	#pj.InsertHuffmanTable(open("IMG_6618.JPG","rb"), open("IMG_6618b.JPG","wb"))
	#pj.Open(open("IMG_6618.JPG","rb"), verbose = 1)

	