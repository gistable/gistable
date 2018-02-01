import sys

a = open(sys.argv[1]).read()

for x in range(0, len(a), 16):
	line = a[x:x+16]
	hexl = ' '.join(y.encode('hex') for y in line)
	hexl += ' '*(47-len(hexl))
	hexl = hexl[:24] + " " + hexl[24:]
	line = line.replace("\n", ".")
	print "%08x" % x, " "+hexl, " |"+line+"|"

print "%08x" % len(a)
