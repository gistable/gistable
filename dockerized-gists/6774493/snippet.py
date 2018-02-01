import os                                                                                                                                                                                               
import zlib
from StringIO import StringIO


ESTIMATED_COMPRESSION_FACTOR = 2 


class UnzipStream(object):
    ''' 
    A file-like wrapper around a gzipped stream that uncompresses as it reads.
    '''
    def __init__(self, stream):
        self.stream = stream
        self.gzip = zlib.decompressobj()
        self.buffered = ''

    def read(self, size=2048):
        buffer = StringIO()
        # If we decompressed more than we read, it's stored in
        # gzip.unconsumed_tail.  See:
        # http://docs.python.org/2/library/zlib.html#zlib.Decompress.unconsumed_tail
        if len(self.gzip.unconsumed_tail) > 0:
            buffer.write(self.gzip.decompress(self.gzip.unconsumed_tail, size))
            if buffer.len == size:
                return buffer.getvalue()
        stream_chunk_size = size / ESTIMATED_COMPRESSION_FACTOR or 1
        while buffer.len < size:
            chunk = self.stream.read(stream_chunk_size)
            if len(chunk) == 0:
                # Input stream is exhausted
                # Flush decompress buffer
                chunk = self.gzip.flush()
                buffer.write(chunk)
                return buffer.getvalue()
            chunk = self.gzip.decompress(chunk, size - buffer.len)
            buffer.write(chunk)
        return buffer.getvalue()

    def readline(self, size=None):
        buffer = StringIO()
        if len(self.buffered) > 0:
            buffer.write(self.buffered[:size])
            self.buffered = self.buffered[size:]
            if buffer.len == size:
                return buffer.getvalue()
        chunk = self.read()
        while len(chunk) > 0 and os.linesep not in chunk:
            buffer.write(chunk)
            chunk = self.read()
        if os.linesep in chunk:
            linesep_pos = chunk.index(os.linesep) + 1
            buffer.write(chunk[:linesep_pos])
            self.buffered = chunk[linesep_pos:]
        return buffer.getvalue()