import random

from datetime import datetime
import struct
import binascii

class SequentialID(object):
    def __init__(self):
        self.rng = random.Random()
        self.reinit()

    def reinit(self):
        prefix_bytes = [self.rng.randint(0, 255) for x in xrange(13)]
        self.prefix = binascii.hexlify(struct.pack('13B', *prefix_bytes))
        self.seq = 0

    def __call__(self):
        if self.seq >= 0xfff000:
            self.reinit()

        self.seq += self.rng.randint(1, 4095)
        return self.prefix + '%06x' % self.seq

class MonotonicID(object):
    def __init__(self):
        self.rng = random.Random()
        self.seq = 0

    def __call__(self):
        if self.seq >= 9590:
            self.seq = 0

        now = datetime.utcnow()
        self.seq += self.rng.randint(1, 409)

        return '%04d%02d%02d%02d%02d%02d%06d%04d' % (
            now.year,
            now.month,
            now.day,
            now.hour,
            now.minute,
            now.second,
            now.microsecond,
            self.seq
        )
