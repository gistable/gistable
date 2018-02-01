    def get_uncompressed_size(self, file):
        fileobj = open(file, 'r')
        fileobj.seek(-8, 2)
        crc32 = gzip.read32(fileobj)
        isize = gzip.read32(fileobj)  # may exceed 2GB
        fileobj.close()
        return isize
