def merge(p, q, r, v):
    w = []
    i, j = p, q
    while i < q and j < r:
        if v[i] <= v[j]:
            w.append(v[i])
            i += 1
        else:
            w.append(v[j])
            j += 1
    while i < q:
        w.append(v[i])
        i += 1
    while j < r:
        w.append(v[j])
        j += 1
    for k in range(p, r): v[k] = w[k-p]
    
def mergesortI(v):
    n = len(v)
    b = 1
    while b < n:
        p = 0
        while p + b < n:
            r = p + 2*b
            if r > n: r = n
            merge(p, p + b, r, v)
            p = p + 2*b
        b = 2*b

from random import shuffle
v = list(range(8))
shuffle(v)
print (v)
mergesortI(v)
print (v)