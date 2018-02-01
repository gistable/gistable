import struct

class bitbuffer:
    # TODO: need reader?
    def __init__(self):
        self.buffer = b''
        self.byte = 0
        self.bit_pos = 7

    def append(self, value, nbits):
        mask = 1 << (nbits - 1)
        while (mask):
            if value & mask:
                self.byte |= (1 << self.bit_pos)
            self.bit_pos -= 1
            mask >>= 1
            if self.bit_pos < 0:
                self.buffer += struct.pack('<B', self.byte)
                self.bit_pos = 7
                self.byte = 0

    def flush(self):
        if self.bit_pos != 7:
            self.buffer += struct.pack('<B', self.byte)

    def get_buffer(self):
        return self.buffer
