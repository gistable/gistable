"""
floyd_warshall_fastest() is a fast Python+NumPy implementation of the Floyd-Warshall algorithm
for finding the shortest path distances between all nodes of a weighted Graph. For more details see
http://en.wikipedia.org/wiki/Floyd-Warshall_algorithm

Tests and time comparisons to slower versions are provided.

Result of test_floyd_warshall_compatibility_on_large_matrix():
    Matrix size: 100
    Slow algorithm (with allocations): 0.726 seconds elapsed
    Running naive inplace algorithm: 0.725 seconds elapsed
    Running partially vectorized algorithm (2 loops): 0.058 seconds elapsed
    Running highly vectorized algorithm (1 loops): 0.003 seconds elapsed

Amit Moscovich Eiger, 22/4/2014.
"""
from numpy import array, asarray, inf, zeros, minimum, diagonal, newaxis
from numpy.random import randint
import time

def check_and_convert_adjacency_matrix(adjacency_matrix):
    mat = asarray(adjacency_matrix)

    (nrows, ncols) = mat.shape
    assert nrows == ncols
    n = nrows

    assert (diagonal(mat) == 0.0).all()

    return (mat, n)

def floyd_warshall_cormen(adjacency_matrix):
    '''An exact implementation of the Floyd-Warshall algorithm as described in Cormen, Leiserson and Rivest.'''
    (mat, n) = check_and_convert_adjacency_matrix(adjacency_matrix)
    
    matrix_list = [mat]
    for k in xrange(n):
        next_mat = zeros((n,n))
        for i in xrange(n):
            for j in xrange(n):
                next_mat[i,j] = min(mat[i,j], mat[i,k] + mat[k,j])
        mat = next_mat
        matrix_list.append(mat)

    return matrix_list[-1]
    
def floyd_warshall_inplace(adjacency_matrix):
    (mat, n) = check_and_convert_adjacency_matrix(adjacency_matrix)

    for k in xrange(n):
        for i in xrange(n):
            for j in xrange(n):
                mat[i,j] = min(mat[i,j], mat[i,k] + mat[k,j])

    return mat

def floyd_warshall_faster(adjacency_matrix):
    from numpy import array, asarray, inf, zeros, minimum, diagonal, newaxis
    (mat, n) = check_and_convert_adjacency_matrix(adjacency_matrix)

    for k in xrange(n):
        for i in xrange(n):
            mat[i,:] = minimum(mat[i,:], mat[i,k] + mat[k,:]) 

    return mat

def floyd_warshall_fastest(adjacency_matrix):
    '''floyd_warshall_fastest(adjacency_matrix) -> shortest_path_distance_matrix

    Input
        An NxN NumPy array describing the directed distances between N nodes.

        adjacency_matrix[i,j] = distance to travel directly from node i to node j (without passing through other nodes)

        Notes:
        * If there is no edge connecting i->j then adjacency_matrix[i,j] should be equal to numpy.inf.
        * The diagonal of adjacency_matrix should be zero.

    Output
        An NxN NumPy array such that result[i,j] is the shortest distance to travel between node i and node j. If no such path exists then result[i,j] == numpy.inf
    '''
    (mat, n) = check_and_convert_adjacency_matrix(adjacency_matrix)

    for k in xrange(n):
        mat = minimum(mat, mat[newaxis,k,:] + mat[:,k,newaxis]) 

    return mat

def test_floyd_warshall_algorithms_on_small_matrix():
    from numpy import array, inf
    INPUT = array([
        [  0.,  inf,  -2.,  inf],
        [  4.,   0.,   3.,  inf],
        [ inf,  inf,   0.,   2.],
        [ inf,  -1.,  inf,   0.]
    ])

    OUTPUT = array([
        [ 0., -1., -2.,  0.],
        [ 4.,  0.,  2.,  4.],
        [ 5.,  1.,  0.,  2.],
        [ 3., -1.,  1.,  0.]])

    assert (floyd_warshall_cormen(INPUT) == OUTPUT).all()
    assert (floyd_warshall_inplace(INPUT) == OUTPUT).all()
    assert (floyd_warshall_faster(INPUT) == OUTPUT).all()
    assert (floyd_warshall_fastest(INPUT) == OUTPUT).all()

class Timer(object):
    def __init__(self):
        self.start_time = time.clock()
    def stop(self):
        print '%.3f seconds elapsed' % (time.clock() - self.start_time)
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.stop()

def test_floyd_warshall_compatibility_on_large_matrix():
    N = 100
    print 'Matrix size:', N
    m = randint(1,100,size=(N,N))
    for i in xrange(N):
        m[i,i] = 0 

    print 'Slow algorithm (with allocations):',
    with Timer():
        res_coremen = floyd_warshall_cormen(m)

    print 'Running naive inplace algorithm:',
    with Timer():
        res_inplace = floyd_warshall_inplace(m)

    print 'Running partially vectorized algorithm (2 loops):',
    with Timer():
        res_faster = floyd_warshall_faster(m)

    print 'Running highly vectorized algorithm (1 loops):',
    with Timer():
        res_fastest = floyd_warshall_fastest(m)

    assert (res_inplace == res_faster).all()
    assert (res_faster == res_fastest).all()
