class BIT:
    def __init__(self, array):
        self.size = len(array)
        self.bit = [0] * (self.size+1)
        self.array = [0] * self.size
        for key, val in enumerate(array):
            self.update(key, val)

    def __getitem__(self, key):
        key += 1
        if key > self.size or key < 0:
            raise ValueError('index out of range')
        res = 0
        while key:
            res += self.bit[key]
            key -= key & -key
        return res

    def update(self, key, delta):
        self.array[key] += delta
        key += 1
        if key > self.size or key < 0:
            raise ValueError('index out of range')
        while key < self.size + 1:
            self.bit[key] += delta
            key += key & -key

    def __setitem__(self, key, val):
        delta = val - self.array[key]
        self.update(key, delta)