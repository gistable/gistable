"""                                                                                                                                                                                                                               
gmaxwell's proof-of-storage                                                                                                                                                                                                       
https://bitcointalk.org/index.php?topic=310323.0                                                                                                                                                                                  
"""
import random
from bisect import bisect_left

H = lambda v: (hash(("1",v)), hash(("2",v)))

def setup(k, seed):
    # Build a (sorted) table of all the index values
    # Return a function that looks up the index, given a query                                                                                                                                
    # O(n log n), n=2^k                                                                                                                                                                                                           
    # k is the height of the tree                                                                                                                                                                                                 
    ctr = [0] # mutable counter                                                                                                                                                                                                   
    global tbl
    tbl = []
    def descend(seed=seed, h=k):
        left,right = H(seed)
        if h == 0:
            tbl.append((left,ctr[0]+0))
            tbl.append((right,ctr[0]+1))
            ctr[0] += 2
        else:
            descend(left, h-1)
            descend(right, h-1)
    descend()
    tbl.sort()
    q,idx = zip(*tbl)
    def respond(chal):
        # O(k) memory accesses in the sorted list
        return idx[bisect_left(q,chal)]
    return respond

def challenge(k, seed):
    # O(k)                                                                                                                                                                                                                        
    idx = random.randint(0,2**k-1)
    def descend(seed=seed, h=k):
        left,right = H(seed)
        if h == 0:
            return left if not (idx & 1) else right
        else:
            if not idx & 2**h: return descend(left, h-1)
            else: return descend(right, h-1)
    return idx, descend()

def test():
    verifierID = "verifier"
    proverID = "prover";
    seed = '%s,%s' % (verifierID, proverID)
    k = 10
    respond = setup(k, seed)
    idx, chal  = challenge(k, seed)
    r = respond(chal)
    print 'idx', idx, 'chal', chal, 'response', r
    assert r == idx