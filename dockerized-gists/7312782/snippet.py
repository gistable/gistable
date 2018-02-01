import struct

def pack_varint(val):
	total = b''
	if val < 0:
		val = (1<<32)+val
	while val>=0x80:
		bits = val&0x7F
		val >>= 7
		total += struct.pack('B', (0x80|bits))
	bits = val&0x7F
	total += struct.pack('B', bits)
	return total

def unpack_varint(buff):
	total = 0
	shift = 0
	val = 0x80
	while val&0x80:
		val = struct.unpack('B', bbuff.read(1))[0]
		total |= ((val&0x7F)<<shift)
		shift += 7
	if total&(1<<31):
		total = total - (1<<32)
	return total