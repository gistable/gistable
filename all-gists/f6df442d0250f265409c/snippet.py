# This will generate a set of bytes to be send via RasPI's SPI interface
# core_freq should be exactly 199
# the SPI divider is 2
# the resulting carrier will appear on 49.75MHz

# Public Domain

from PIL import Image
from sys import argv, stdout

SYNC = "0011" * 100
BACKPORCH = "0001" * 200
SYNC_L = ("10"*1492) + ("00"*92)
SYNC_S = ("10"*92) + ("00"*1492)

BLACK = "1000100010001000"
WHITE = "1010101010101010"

bits = ""

if len(argv) != 2:
	print "Usage: %s {imgfile} > outfile.bin"
	exit(1)

img = Image.open(argv[1])
w, h = img.size

if (w!=323) or (h!=152):
	print "Invalid image size, should be 323x152"
	img.close()
	exit(1)

pixels = img.load()

bits += SYNC_L + SYNC_L + SYNC_L + SYNC_L + SYNC_L + \
	 SYNC_S + SYNC_S + SYNC_S + SYNC_S + SYNC_S

for x in xrange(w):
	bits += SYNC + BACKPORCH
	for i in xrange(8):
		for y in xrange(h):
			level = BLACK if (pixels[x, y][1] < 128) else WHITE
			bits += (level*2)

bits += SYNC_S + SYNC_S + \
	SYNC_S + SYNC_S + \
	SYNC_S + SYNC_S

bits *= 8

i = hex(int(bits, 2))[2:].replace("L", "").decode("hex")
stdout.write(i)