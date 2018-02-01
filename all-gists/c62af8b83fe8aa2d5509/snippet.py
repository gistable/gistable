#!/usr/bin/python

text = '22T189RSNH11T .264749,"OIO""O"O,RSNDLHNLDHDSDSHSDCCCRCCNHNNK.ETFGWU .E0E T6839937643?!,"O'
text += '!RLHDSRSCSDLNCCCCCDNUV1E  RCHN2E0E  68495RSNNRSRRLHNCLHDCDSDSDNCCNCCCH,"?,HJQKV"???,DRLCCC'

#text = '68753RCNRLNYYWGGWUFMGKXKXQZKXJZZKK'

register = [1,1,1,1,1,1,1,0]
spoke = 0
spokes = [
	' ET.012',
	'3456789',
	',?!"AOI',
	'NSHRDLC',
	'UMWFGYP',
	'BVKJXQZ'
]

def reset_spoke():
	global spoke
	spoke = 0

def next_spoke():
	global spoke
	spoke = (spoke + 1) % 6

def int2bin(int):
	return bin(int)[2:].zfill(3)

def shift():
	global register
	register.append(register[0] ^ register[1])
	register = register[1:]

def cipher(byte):
	result = str(register[7] ^ int(byte[0])) + \
	         str(register[6] ^ int(byte[1])) + \
	         str(register[5] ^ int(byte[2]))
	shift()
	return result

def lookup(bin):
	if bin == '000':
		next_spoke()
		return ''
	return spokes[spoke][int(bin, 2) - 1]

def crypt(bytes):
	reset_spoke()
	return map(cipher, bytes)

def encode(str):
	reset_spoke()
	bytes = []
	for char in str:
		byte = ""
		while byte == "":
			for x in spokes[spoke]:
				if x == char:
					byte = int2bin(spokes[spoke].find(char) + 1)
					break
			if byte == "":
				bytes.append('000')
				next_spoke()
		bytes.append(byte)
	return bytes

def decode(bytes):
	reset_spoke()
	temp = ""
	for byte in bytes:
		temp += lookup(byte)
	return temp

for i in range(0, 255):
	temp = bin(i)[2:].zfill(8)
	register = []
	for bit in temp:
		register.append(int(bit))
	#print register
	print decode(crypt(encode(text)))