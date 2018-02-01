import hashlib
import collections
import sys

# Functions have types, of form [A @] [a] -> [b] [@ B]
# where A and B are coeffects & effects
# Any part might be omitted if null

def prf(val): # str -> seq(bool)
    m = hashlib.sha512()
    m.update(val)
    while True:
        for c in m.digest():
            for i in range(8):
                yield (ord(c) & (1 << i)) > 0
        m.update("step")

# HTree = HNode | HLeaf

HNode = collections.namedtuple("HNode", ["hash", "l", "r", "size"])
def hnode_make(l, r): # HTree × HTree -> HTree
    m = hashlib.sha512()
    m.update(l.hash)
    m.update(r.hash)
    h = m.digest()
    return HNode(h, l, r, l.size + r.size)

HLeaf = collections.namedtuple("HLeaf", ["hash", "val", "size"])
def hleaf_make(val): # str -> HTree
    m = hashlib.sha512()
    m.update(val)
    h = m.digest()
    return HLeaf(h, val, 1)

def putnode(h): # HTree -> @ io
    if isinstance(h, HLeaf):
        sys.stdout.write(h.val)
    else:
        sys.stdout.write("(")
        putnode(h.l)
        sys.stdout.write(" ")
        putnode(h.r)
        sys.stdout.write(")")

def heightnode(h): # HTree -> int
    if isinstance(h, HLeaf):
        return 1
    else:
        return 1 + max(heightnode(h.l), heightnode(h.r))

class SeqHash:
    def __init__(self): # self @ -> SeqHash
        self.hashes = []
    
    @staticmethod
    def _join(roots, prfs=None):
        if prfs is None:
            prfs = [prf(r.hash) for r in roots]
        out = []
        outp = []
        first = [next(p) for p in prfs]
        last = None
        lastp = None
        for b, root, p in zip(first, roots, prfs):
            if b:
                if last:
                    out.append(last)
                    outp.append(p)
                last = root
                lastp = p
            else:
                if last:
                    out.append(hnode_make(last, root))
                    outp.append(prf(out[-1].hash))
                else:
                    out.append(root)
                    outp.append(p)
                last = None
                lastp = None

        if last:
            out.append(last)
            outp.append(lastp)
        
        if len(out) < len(roots):
            return SeqHash._join(out, outp)
        else:
            return out

    def compress(self): # self @ -> @ self
        self.hashes = SeqHash._join(self.hashes)

    def append_left(self, val): # self @ str -> @ self
        leaf = hleaf_make(val)
        self.hashes = self.hashes + [leaf]
        self.compress()

    def append_right(self, val): # self @ str -> @ self
        leaf = hleaf_make(val)
        self.hashes = [leaf] + self.hashes
        self.compress()

    @staticmethod
    def firstdiff(node1, node2): # HTree × HTree -> µ t: "r" × t | "l" × t | "t" × HLeaf × HLeaf
        if node1.hash == node2.hash:
            return None
        elif isinstance(node1, HNode) and isinstance(node2, HNode):
            if node1.l.hash == node2.l.hash:
                return ("r", SeqHash.firstdiff(node1.r, node2.r))
            else:
                return ("l", SeqHash.firstdiff(node1.l, node2.l))
        else:
            while isinstance(node1, HNode): node1 = node1.l
            while isinstance(node2, HNode): node2 = node2.l
            return ("t", node1, node2)
    
    def put(self): # self @ -> @ io
        for r in self.hashes:
            putnode(r)
            sys.stdout.write(" ")
        print
    
    @property
    def height(self): # self @ -> int
        return max(map(heightnode, self.hashes))
    
    def __getitem__(self, i): # self @ int -> HLeaf
        for r in self.hashes:
            if r.size > i:
                break
            else:
                i -= r.size

        while True:
            if isinstance(r, HLeaf):
                return r
            else:
                if r.l.size > i:
                    r = r.l
                else:
                    i -= r.l.size
                    r = r.r
    
    def __len__(self): # self @ -> int
        return sum(r.size for r in self.hashes)

def test():
    N = 1000
    import math
    L = 2 * math.log(N) / math.log(2)

    s = SeqHash()
    for i in range(N):
        if i % 6 in (0, 1, 4):
            s.append_left(str(i))
        else:
            s.append_right(str(i))

    print s.height
    assert len(s) == N, "Wrong length"
    assert s.height < L, "Too tall"
    assert len(s.hashes) < L, "Too wide"
    assert all(s[i].val == str(i) for i in range(len(s))), "Indexing broken"

