import struct
import zlib
import itertools

class bitstream(object):
    def __init__(self, buf):
        self.buf = buf
        self.i = 0
        self.rem = 0
        self.n = 0

    def fetch(self, nbits):
        while self.n < nbits:
            self.rem = (self.rem << 8) | ord(self.buf[self.i])
            self.n += 8
            self.i += 1
        retval = (self.rem >> (self.n - nbits)) & ((1 << nbits) - 1)
        self.n -= nbits
        self.rem &= (1 << self.n) - 1
        return retval

def get_swf_rect(swf):
    if isinstance(swf, basestring):
        swf = open(swf)

    data = swf.read()

    signature, version, size = struct.unpack('<3s1b1I', data[0:8])
    if signature == 'CWS':
        body = zlib.decompress(data[8:])
    else:
        body = data[8:]
    if size != len(body) + 8:
        raise "invalid format"
    bs = bitstream(body)
    nbits = bs.fetch(5)
    return (bs.fetch(nbits), bs.fetch(nbits), bs.fetch(nbits), bs.fetch(nbits))

def rect_to_size(rect):
    return ((rect[1] - rect[0]), (rect[3] - rect[2]))

def in_pixel(values):
    return tuple((value / 20 for value in values))

if __name__ == '__main__':
    import sys
    print in_pixel(rect_to_size(get_swf_rect(sys.argv[1])))
