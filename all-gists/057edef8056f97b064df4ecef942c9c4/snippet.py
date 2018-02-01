import numpy as np

class InvertedIndex(object):

    def __init__(self, x):
        self.J = np.argsort(x)
        D = np.ediff1d(x[self.J], to_begin=1, to_end=1)
        self.I = np.repeat(np.arange(len(D)), D)

    def __getitem__(self, k):
        return self.J[self.I[k]:self.I[k + 1]]


if __name__ == '__main__':
    x = np.array([3, 2, 5, 2, 4, 0, 2, 5])
    print('input :', x)
    iidx = InvertedIndex(x)
    for k in range(max(x) + 1):
        print('query', k, ':', iidx[k])

# > python iidx.py
# input : [3 2 5 2 4 0 2 5]
# query 0 : [5]
# query 1 : []
# query 2 : [1 3 6]
# query 3 : [0]
# query 4 : [4]
# query 5 : [2 7]
