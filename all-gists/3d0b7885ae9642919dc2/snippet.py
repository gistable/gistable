import sys

ps_shellcode = '@('

with open(sys.argv[1], 'rb') as shellcode:
	byte = shellcode.read(1)
	while byte != '':
		ps_shellcode += '0x{}, '.format(byte.encode('hex'))
		byte = shellcode.read(1)

ps_shellcode = ps_shellcode[:-2] #get rid of the last whitespace and comma
ps_shellcode += ')'

print ps_shellcode