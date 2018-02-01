import zlib
import struct
import sys

pvr = sys.argv[1]
ccz = pvr + ".ccz"

pvr = open(pvr).read()
ccz = open(ccz, "wb")

ccz.write(struct.pack(">4sHHII", "CCZ!", 0, 1, 0, len(pvr)))
ccz.write(zlib.compress(pvr))
ccz.close()
