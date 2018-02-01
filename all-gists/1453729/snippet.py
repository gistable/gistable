def hashfn(item):
    h = hash(item)
    return (1 << (h%64)) | (1 << (h/64%64))

def mask(val):
    return bin(hashfn(val))[2:]

class CountingBloom(object):
    def __init__(self):
        self.items = [0] * 64
    def add(self, item):
        bits = mask(item)
        for index, bit in enumerate(bits):
            if bit == '1':
                self.items[index] += 1
    def query(self, item):
        bits = mask(item)
        for index, bit in enumerate(bits):
            if bit == '1' and self.items[index] == 0:
                return False
        return True
    def remove(self, item):
        bits = mask(item)
        for index, bit in enumerate(bits):
            if bit == '1' and self.items[index]:
                self.items[index] -= 1

bloom = CountingBloom()
args = ('foo', 'bar', 'baz')
for arg in args:
    bloom.add(arg)
    print ', '.join(str(bloom.query(arg)) for arg in args)
for arg in args:
    bloom.remove(arg)
    print ', '.join(str(bloom.query(arg)) for arg in args)


# $ python bloom.py 
# True, False, False
# True, True, False
# True, True, True
# False, True, True
# False, False, True
# False, False, False
# $