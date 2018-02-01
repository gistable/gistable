class KeyifyList(object):
    def __init__(self, inner, key):
        self.inner = inner
        self.key = key

    def __len__(self):
        return len(self.inner)

    def __getitem__(self, k):
        return self.key(self.inner[k])


if __name__ == '__main__':
    import bisect
    L = [(0, 0), (1, 5), (2, 10), (3, 15), (4, 20)]
    assert bisect.bisect_left(KeyifyList(L, lambda x: x[0]), 3) == 3
    assert bisect.bisect_left(KeyifyList(L, lambda x: x[1]), 3) == 1