import numpy as np
from numpy.random import uniform


def update(S, k, v):
    "Update value position `k` in time O(log n)."
    d = S.shape[0]
    i = d//2 + k
    S[i] = v
    while i > 0:
        i //= 2
        S[i] = S[2*i] + S[2*i + 1]


def sumheap(w):
    "Create sumheap from weights `w`."
    n = w.shape[0]

    # About the datastructure: Bottom-most level of the heap has size n' =
    # next-power-of-two(n). The number of internal nodes in the tree is n'-1. We
    # have a dummy node at position zero to make indexing math simpler. So, we
    # allocate twice the size of the bottom level to fit internal nodes. Thus,
    # the overal data structure is <4*n in the worst case because the next power
    # of two <2n and then we have another factor of two for internal nodes.
    d = int(2**np.ceil(np.log2(n)))
    S = np.zeros(2*d)

    # O(n) version (faster than calling update n times => O(n log n))
    S[d:d+n] = w
    for i in reversed(range(1, d)):
        S[i] = S[2*i] + S[2*i + 1]

    return S


def check(S, i):
    "Check heap invariant."
    d = S.shape[0]
    if i >= d//2:   # only checks internal nodes.
        return
    assert S[i] == S[2*i] + S[2*i + 1]
    check(S, 2*i)
    check(S, 2*i + 1)


def dump(S):
    "Print heap for debugging."
    for i in range(int(np.ceil(np.log2(len(S))))):
        print 'depth', i, S[2**i:2**(i+1)]


def sample(w, u):
    "Ordinary sampling method, O(n) to build heap, O(log n) per sample after that."
    c = w.cumsum()
    return c.searchsorted(u * c[-1])


def hsample(S, u):
    "Sample from sumheap, O(log n) per sample."
    offset = S.shape[0]//2  # number of internal nodes.
    # random probe
    p = S[1] * u
    # Use binary search to find the index of the largest CDF (represented as a
    # heap) value that is less than a random probe.
    i = 1
    while i < offset:
        # Determine if the value is in the left or right subtree.
        i *= 2
        left = S[i]
        if p > left:
            # Value is in right subtree. Subtract mass under left subtree.
            p -= left
            i += 1
    return i - offset


def main():
    for n in np.random.choice(range(1, 100), size=10):
        print n
        w = np.round(uniform(0, 10, size=n), 1)
        S = sumheap(w)
        check(S, 1)
        for _ in range(100):
            # test uses same random number because the methods should be identical up to ties.
            u = uniform()
            p1 = sample(w, u)
            p2 = hsample(S, u)
            assert p1 == p2
            # change a random value in the weight array
            c = np.random.randint(n)
            v = uniform(10)
            w[c] = v
            update(S, c, v)
            check(S, 1)


if __name__ == '__main__':
    main()
