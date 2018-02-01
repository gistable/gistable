# coding: utf-8
'''
In [1]: import cos

In [2]: u = cos.u

In [3]: v = cos.v

In [4]: timeit cos.vector_cos(u, v)
10000 loops, best of 3: 56 µs per loop

In [5]: timeit cos.vector_cos2(u, v)
10000 loops, best of 3: 72.2 µs per loop

In [6]: timeit cos.vector_cos3(u, v)
1000 loops, best of 3: 348 µs per loop

In [7]: timeit cos.vector_cos4(u, v)
10000 loops, best of 3: 139 µs per loop

In [8]: timeit cos.vector_cos5(u, v)
10000 loops, best of 3: 48 µs per loop

In [9]: timeit cos.vector_cos6(u, v)
10000 loops, best of 3: 59.4 µs per loop
'''
import math
import random
import operator
import itertools
from scipy.spatial.distance import cosine as _vector_cos2
from sklearn.metrics.pairwise import cosine_similarity as _vector_cos3

####

def vector_dot(a, b):
    s = 0.0
    for i in range(len(a)):
        s += (a[i] * b[i])
    return s


def vector_length(a):
    return math.sqrt(vector_dot(a, a))


def vector_cos(a, b):
    return vector_dot(a, b) / (vector_length(a) * vector_length(b))


####

def vector_cos2(u, v):
    return 1.0 - _vector_cos2(u, v)


####

def vector_cos3(u, v):
    return _vector_cos3(u, v)[0][0]
    

####

def dot_product(v1, v2):
    return sum(map(lambda x: x[0] * x[1], itertools.izip(v1, v2)))


def vector_cos4(v1, v2):
    prod = dot_product(v1, v2)
    len1 = math.sqrt(dot_product(v1, v1))
    len2 = math.sqrt(dot_product(v2, v2))
    return prod / (len1 * len2)


####

def dot_product2(v1, v2):
    return sum(map(operator.mul, v1, v2))


def vector_cos5(v1, v2):
    prod = dot_product2(v1, v2)
    len1 = math.sqrt(dot_product2(v1, v1))
    len2 = math.sqrt(dot_product2(v2, v2))
    return prod / (len1 * len2)

u = [random.random() for i in range(100)]
v = [random.random() for i in range(100)]


####

def dot_product3(v1, v2):
    return sum(
        (a + b for (a, b) in itertools.izip(v1, v2)),
        0
    )


def vector_cos6(v1, v2):
    prod = dot_product3(v1, v2)
    len1 = math.sqrt(dot_product3(v1, v1))
    len2 = math.sqrt(dot_product3(v2, v2))
    return prod / (len1 * len2)


u = [random.random() for i in range(100)]
v = [random.random() for i in range(100)]

def main():
    for fn in [
        vector_cos, vector_cos2, vector_cos3,
        vector_cos4, vector_cos5
    ]:
        print fn.__name__, fn(u, v)


if __name__ == '__main__':
    main()