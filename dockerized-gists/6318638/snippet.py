class RottenGzipFile(object):
    """
    Standard library GzipFile replacement, since it has several issues with
    files containing extra data after compressed stream.

    See http://stackoverflow.com/questions/4928560/how-can-i-work-with-gzip-files-which-contain-extra-data
    for details.

    This class does not implement everything usually included in file-like 
    objects.
    """

    def __init__(self, name):
        self.name = name
        self.f = open(self.name, 'r')
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)

        # Before we can decompress anything, we must process the GZIP file
        # header. Since its length can vary, we must parse the FLAGS field.
        # See the RFC: http://www.gzip.org/zlib/rfc-gzip.html#file-format

        header = self.f.read(10)
        flags = ord(header[3])

        if flags & 0x4:
            # FLG.FEXTRA set
            extra_len = ord(self.f.read(1))
            extra_len += ord(self.f.read(1)) << 8
            self.f.seek(extra_len, os.SEEK_CUR)

        if flags & 0x8:
            # FLG.FNAME set
            c = self.f.read(1)
            while c != '\0':
                c = self.f.read(1)

        if flags & 0x10:
            # FLG.FCOMMENT set
            c = self.f.read(1)
            while c != '\0':
                c = self.f.read(1)

        if flags & 0x2:
            # FLG.FHCRC set
            self.f.seek(2, os.SEEK_CUR)

    def read(self, max_length=None):
        if max_length:
            # deflate might expand data in bad cases, thus *2
            return self.decompressor.decompress(
                self.decompressor.unconsumed_tail + self.f.read(max_length * 2),
                max_length)

        else:
            return self.decompressor.decompress(
                self.decompressor.unconsumed_tail + self.f.read())

    def close(self):
        self.f.close()