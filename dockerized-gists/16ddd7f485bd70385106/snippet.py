
import array
class WeightedQuickUnion:
    def __init__(self, N):
        self.count = N
        self.id = array.array('i', range(N))
        self.size = array.array('i', [1] * N)
    
    def connected(self, p, q):
        return self.find(p) == self.find(q)
    
    def count(self):
        return self.count
    
    def find(self, p):
        while (p != self.id[p]):
            p = self.id[p]
        return p
    
    def get(self, p):
        return self.id[p]
    
    def union(self, p, q):
        rootP = self.find(p)
        rootQ = self.find(q)
        if (rootP == rootQ):
            return
        
        if (self.size[rootP] < self.size[rootQ]):
            self.id[rootP] = rootQ
            self.size[rootQ] += self.size[rootP]
        else:
            self.id[rootQ] = rootP
            self.size[rootP] += self.size[rootQ]
        self.count += 1


# %% Percolation
class Percolation:
    def __init__(self, N):
        self.uf = WeightedQuickUnion(N*N+2)
        self.grid = [[False for x in range(N)] for x in range(N)]
        self.vTop = 0
        self.vBottom = N*N+1
        
        if (N == 1):
            return
        
        for k in range(1, N+1):
            self.uf.union(self.xyTo1D(N, k), self.vBottom)
            self.uf.union(self.xyTo1D(1, k), self.vTop)
    
    def open(self, i, j):
        self.grid[i-1][j-1] = True
        if (len(self.grid) == 1):
            self.uf.union(self.xyTo1D(i, j), self.vBottom)
            self.uf.union(self.xyTo1D(i, j), self.vTop)
        
        p = self.xyTo1D(i, j)
        self.unionNeighbor(p, i-1, j)
        self.unionNeighbor(p, i, j-1)
        self.unionNeighbor(p, i, j+1)
        self.unionNeighbor(p, i+1, j)
    
    def isOpen(self, i , j):
        return self.grid[i-1][j-1]
    
    def isFull(self, i, j):
        return self.isOpen(i, j) and self.uf.connected(self.vTop, self.xyTo1D(i,j))
    
    def percolates(self):
        return self.uf.connected(self.vTop, self.vBottom)
    
    def valid(self, i):
        N = len(self.grid)
        return (i > 0 and i <= N)
    
    def xyTo1D(self, i, j):
        N = len(self.grid)
        # Error checking with valid
        return (i-1) * N + j
    
    def unionNeighbor(self, p, i, j):
        if (not (self.valid(i) and self.valid(j))):
            return
        
        if (self.isOpen(i, j)):
            self.uf.union(p, self.xyTo1D(i, j))


# %% Percolation Stats
import math
import random

class PercolationStats:
    def __init__(self, N, T):
        self.trials = T
        self.run = [self.simulation(N) for x in range(T)]
        self.mu = sum(self.run) / T
        self.sd = sum([(r-self.mu)**2 for r in self.run]) / T
    
    def mean(self):
        return self.mu
    
    def stddev(self):
        return self.sd
    
    def confidenceLo(self):
        return self.mu - ((1.96 * self.sd) / math.sqrt(self.trials))
    
    def confidenceHi(self):
        return self.mu - ((1.96 * self.sd) / math.sqrt(self.trials))

    def simulation(self, N):
        Perc = Percolation(N)
        count = 0
        while (not Perc.percolates()):
            i = random.randint(1, N)
            j = random.randint(1, N)
            if (not Perc.isOpen(i, j)):
                Perc.open(i, j)
                count += 1
        
        return count * 1.0 / (N**2)
