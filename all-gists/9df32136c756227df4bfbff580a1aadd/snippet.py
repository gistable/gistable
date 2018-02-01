import binascii
import struct


class Punk(object):

    _END_CHUNK_TYPE = 'IEND'
    _PUNK_CHUNK_TYPE = 'puNk'
    _MAX_BYTES = 2147483647
    _chunks = dict()

    def __init__(self):

        self._mode = None
        self._file = None
        self._output = None
        self._bytes_to_hide = None

        self._bytes_read = 0

    def decode(self, input_file, output_file):
        self._mode = 'decode'
        self._file = open(input_file, 'rb+')
        self._output = open(output_file, 'wb+')

        # First move cursor past the signature
        self._read_bytes(8)

        # Start reading chunks
        self._read_next_chunk()

    def encode(self, input_file, bytes_to_hide):

        self._mode = 'encode'
        self._file = open(input_file, 'rb+')
        self._bytes_to_hide = bytes_to_hide

        # First move cursor past the signature
        self._read_bytes(8)

        # Start reading chunks
        self._read_next_chunk()

    def _read_bytes_as_hex(self, position):

        return self._read_bytes(position).encode('hex')

    def _read_bytes_as_ascii(self, position):

        return self._read_bytes(position).encode('ascii')

    def _read_bytes_as_int(self, position):

        return int(self._read_bytes_as_hex(position), 16)

    def _read_bytes(self, byte_count):

        self._bytes_read += byte_count
        return self._file.read(byte_count)

    def _rewind_bytes(self, byte_count):

        self._bytes_read -= byte_count
        self._file.seek(self._bytes_read)

    def _inject_punk_chunk(self):

        # Move back 8 bytes.
        self._rewind_bytes(8)

        chunk_size = len(self._bytes_to_hide)
        print 'Hiding', (chunk_size / 1024), 'kB (', chunk_size, 'bytes)'

        # Create a temporary byte array for the CRC check.
        tmp_bytes = bytearray()

        # First write the chunk type
        tmp_bytes.extend(bytearray(self._PUNK_CHUNK_TYPE))

        # Now write the bytes of whatever we're trying to hide
        tmp_bytes.extend(self._bytes_to_hide)

        print 'Injecting punk chunk'

        # Write the chunk size
        self._file.write(bytearray(struct.pack('!i', chunk_size)))

        # And the type
        self._file.write(bytearray(self._PUNK_CHUNK_TYPE))

        self._file.write(self._bytes_to_hide)

        crc = binascii.crc32(tmp_bytes)
        self._file.write(bytearray(struct.pack('!i', crc)))

        # Write the end chunk. Start with the size.
        self._file.write(bytearray(struct.pack('!i', 0)))
        # Then the chunk type.
        self._file.write(bytearray(self._END_CHUNK_TYPE))

        print 'Punk chunk injected'

    def _read_next_chunk(self):

        chunk_size = self._read_bytes_as_int(4)
        print 'Chunk size:', chunk_size

        chunk_type = self._read_bytes_as_ascii(4)
        print 'Chunk type:', chunk_type

        if self._mode == 'encode' and chunk_type == self._END_CHUNK_TYPE:

            self._inject_punk_chunk()

            print 'Reached EOF'
            self._file.close()

            return

        content = self._read_bytes(chunk_size)

        crc = self._read_bytes_as_hex(4)
        print 'CRC:', crc

        if self._mode == 'decode' and chunk_type == self._PUNK_CHUNK_TYPE:

            print "Found a punk chunk", len(content), "bytes. Writing to file"
            self._output.write(bytearray(content))
            self._output.close()
            self._file.close()

            return

        self._read_next_chunk()