import numpy as np
def insert_bit(array, index):
    inner = (index % 64)
    index //= 64
    array[index] |= (1 << inner)
    

def is_set(array, index):
    inner = (index % 64)
    index //= 64
    return array[index] & (1 << inner)


class BloomFilter(object):
    def __init__(self, N, Nbits):
        self.Nbits = Nbits
        self.bloom = np.zeros(Nbits//64 + bool(Nbits % 64), np.uint64)
        self.k = int(np.round(.7 *Nbits/N))

    def hash(self, s, index):
        return (hash(s + ('x' * index)) % self.Nbits)

    def insert(self, s):
        for h in xrange(self.k):
            insert_bit(self.bloom, self.hash(s, h))

    def __contains__(self, s):
        for h in xrange(self.k):
            if not is_set(self.bloom, self.hash(s, h)):
                return False
            return True
