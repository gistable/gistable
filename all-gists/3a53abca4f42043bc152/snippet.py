import sys
import os
import struct
import zlib
__author__ = 'Tachi'


class TOSZipDecrypter:
    @staticmethod
    def _GenerateCRCTable():
        """Generate a CRC-32 table.

        ZIP encryption uses the CRC32 one-byte primitive for scrambling some
        internal keys. We noticed that a direct implementation is faster than
        relying on binascii.crc32().
        """
        poly = 0xedb88320
        table = [0] * 256
        for i in range(256):
            crc = i
            for j in range(8):
                if crc & 1:
                    crc = ((crc >> 1) & 0x7FFFFFFF) ^ poly
                else:
                    crc = ((crc >> 1) & 0x7FFFFFFF)
            table[i] = crc
        return table
    crctable = _GenerateCRCTable.__func__()

    def _crc32(self, ch, crc):
        """Compute the CRC32 primitive on one byte."""
        return ((crc >> 8) & 0xffffff) ^ self.crctable[(crc ^ ord(ch)) & 0xff]

    def __init__(self, pwd):
        self.key0 = 305419896
        self.key1 = 591751049
        self.key2 = 878082192
        for p in pwd:
            self._UpdateKeys(p)

    def _UpdateKeys(self, c):
        self.key0 = self._crc32(c, self.key0)
        self.key1 = (self.key1 + (self.key0 & 0xFF)) & 0xFFFFFFFF
        self.key1 = (self.key1 * 134775813 + 1) & 0xFFFFFFFF
        self.key2 = self._crc32(chr((self.key1 >> 24) & 0xFF), self.key2)

    def decrypt(self, buf):
        result = list()
        for i in range(len(buf)):
            if not i % 2:
                result.append(self(buf[i]))
            else:
                result.append(buf[i])
        return ''.join(result)

    def __call__(self, c):
        """Decrypt a single character."""
        c = ord(c)
        k = self.key2 | 2
        c = c ^ (((k * (k^1)) >> 8) & 255)
        c = chr(c)
        self._UpdateKeys(c)
        return c


class File(object):
    NSIZE = 0
    CRC = 0
    ZSIZE = 0
    SIZE = 0
    OFFSET = 0
    CSIZE = 0
    comment = ""
    name = ""

    def __init__(self, NSIZE, CRC, ZSIZE, SIZE, OFFSET, CSIZE, comment, name):
        self.NSIZE = NSIZE
        self.CRC = CRC
        self.ZSIZE = ZSIZE
        self.SIZE = SIZE
        self.OFFSET = OFFSET
        self.CSIZE = CSIZE
        self.comment = comment
        self.name = name


files = list()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "need argument"
        exit()
    with open(sys.argv[1], 'rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(-0x18, os.SEEK_END)
        file_numb, table_offset, flag = struct.unpack("<HIH", f.read(8))
        f.seek(table_offset, os.SEEK_SET)
        for i in range(file_numb):
            field = struct.unpack("<HIIIIH", f.read(20))
            field = list(field)
            field += struct.unpack("{0}s{1}s".format(field[5], field[0]), f.read(field[0]+field[5]))
            files.append(File(*field))
        for i in files:
            print i.comment, i.name
            f.seek(i.OFFSET, os.SEEK_SET)
            buf = f.read(i.ZSIZE)
            if i.ZSIZE != i.SIZE:
                dec = TOSZipDecrypter("ofO1a0ueXA? [\xFFs h %?")
                buf = dec.decrypt(buf)
                buf = zlib.decompress(buf, -zlib.MAX_WBITS)
            name = "{1}/{2}".format(sys.argv[1][:-4],i.comment[:-4],i.name)
            if '/' in name:
                if not os.path.exists(os.path.dirname(name)):
                    os.makedirs(os.path.dirname(name))
            with open(name, 'wb') as out:
                out.write(buf)
