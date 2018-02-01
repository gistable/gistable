#!/usr/bin/env/python
#
# Little script to play around with the code and
# data of H. Tropf, H. Herzog's paper 1981 paper
#    "Multidimensional Range Search in Dynamically
#    Balanced Trees".
#
# Thanks to Bernhard Herzog (unrelated to H. Herzog)
# for having a second look at the code.
#

class Node(object):

    def __init__(self, x, y, left = None, right = None):
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.zcode = z_encode(x, y)

    def inorder(self, visit):
        n = self
        while n is not None:
            if n.left: n.left.inorder(visit)
            visit(n)
            n = n.right

    def naiv_search(self, x1, y1, x2, y2, visit):
        minz, maxz = z_encode(x1, y1), z_encode(x2, y2)
        def recurse(node):
            while node is not None:
                if node.zcode < minz:
                    node = node.right
                elif node.zcode > maxz:
                    node = node.left
                else: # minz <= node.zcode <= maxz:
                    recurse(node.left)
                    if x1 <= node.x <= x2 and y1 <= node.y <= y2:
                        visit(node)
                    node = node.right
        recurse(self)

    def search(self, x1, y1, x2, y2, visit, LITMAX, BIGMIN):
        z1, z2 = z_encode(x1, y1), z_encode(x2, y2)
        def recurse(node, minz, maxz):
            if node is None: return
            zcode = node.zcode
            if   zcode < minz: recurse(node.right, minz, maxz)
            elif zcode > maxz: recurse(node.left, minz, maxz)
            else: # minz <= zcode <= maxz:
                if x1 <= node.x <= x2 and y1 <= node.y <= y2:
                    recurse(node.left, minz, zcode)
                    visit(node)
                    recurse(node.right, zcode, maxz)
                else:
                    recurse(node.left, minz, LITMAX(z1, z2, zcode))
                    recurse(node.right, BIGMIN(z1, z2, zcode), maxz)
        recurse(self, z1, z2)

    def __cmp__(self, other):
        return cmp(self.zcode, other.zcode)

    def __repr__(self):
        return "(%d, %d): %d" % (self.x, self.y, self.zcode)

def build_tree(nodes, lo = 0, hi = None):
    if hi is None: hi = len(nodes)-1
    if hi < lo: return None
    mid = (lo+hi)/2
    node = nodes[mid]
    node.left = build_tree(nodes, lo, mid-1)
    node.right = build_tree(nodes, mid+1, hi)
    return node

def z_encode(x, y):
    result = 0
    mask = 1
    b = 1
    while mask < 1 << 20:
        if y & mask: result |= b
        b <<= 1
        if x & mask: result |= b
        b <<= 1
        mask <<= 1
    return result

def z_decode(zcode):
    x, y = 0, 0
    b = 1
    mask = 1
    while mask < 1 << 20:
        if zcode & mask: y |= b
        mask <<= 1
        if zcode & mask: x |= b
        mask <<= 1
        b <<= 1
    return x, y

def stupid_litmax(minz, maxz, zcode):
    x1, y1 = z_decode(minz)
    x2, y2 = z_decode(maxz)
    cand = minz
    for x in range(x1, x2+1):
        for y in range(y1, y2+1):
            z = z_encode(x, y)
            if z < zcode and z > cand:
                cand = z
    return cand

def stupid_bigmin(minz, maxz, zcode):
    x1, y1 = z_decode(minz)
    x2, y2 = z_decode(maxz)
    cand = maxz
    for x in range(x1, x2+1):
        for y in range(y1, y2+1):
            z = z_encode(x, y)
            if z > zcode and z < cand:
                cand = z
    return cand

_000_ = 0
_001_ = 1
_010_ = 1 << 1
_011_ = (1 << 1)|1
_100_ = 1 << 2
_101_ = (1 << 2)|1

MASK = 0xaaaaa # hex(int('10'*10, 2))

FULL = 0xffffffff

def setbits(p, v):
    mask = (MASK >> (19-p)) & (~(FULL << p) & FULL)
    return (v | mask) & ~(1 << p) & FULL

def unsetbits(p, v):
    mask = ~(MASK >> (19-p)) & FULL
    return (v & mask) | (1 << p)

def clever_litmax(minz, maxz, zcode):
    litmax = minz
    for p in range(19, -1, -1):
        mask = 1 << p
        v = (zcode & mask) and _100_ or _000_
        if minz & mask: v |= _010_
        if maxz & mask: v |= _001_

        if v == _001_:
            maxz = setbits(p, maxz)
        elif v == _011_:
            break
        elif v == _100_:
            litmax = maxz
            break
        elif v == _101_:
            litmax = setbits(p, maxz)
            minz = unsetbits(p, minz)
    return litmax

def clever_bigmin(minz, maxz, zcode):
    bigmin = maxz
    for p in range(19, -1, -1):
        mask = 1 << p
        v = (zcode & mask) and _100_ or _000_
        if minz & mask: v |= _010_
        if maxz & mask: v |= _001_

        if v == _001_:
            bigmin = unsetbits(p, minz)
            maxz = setbits(p, maxz)
        elif v == _011_:
            bigmin = minz
            break
        elif v == _100_:
            break
        elif v == _101_:
            minz = unsetbits(p, minz)
    return bigmin

def appender(nodes):
    def append(node):
        nodes.append(node)
    return append

def main():
    nodes = [Node(x, y) for x in range(9) for y in range(17)]
    nodes.sort()

    root = build_tree(nodes)
    all_nodes = []
    root.inorder(appender(all_nodes))

    # check tree
    print "Tree correct:", all_nodes == nodes

    naiv_result = []
    root.naiv_search(3, 5, 5, 10, appender(naiv_result))

    print len(naiv_result)
    print naiv_result

    stupid_result = []
    root.search(3, 5, 5, 10, appender(stupid_result),
                stupid_litmax, stupid_bigmin)

    print len(stupid_result)
    print stupid_result

    print "stupid == naiv:", stupid_result == naiv_result

    clever_result = []
    root.search(3, 5, 5, 10, appender(clever_result),
                clever_litmax, clever_bigmin)

    #print len(clever_result)
    #print clever_result

    print "clever == naiv:", clever_result == naiv_result
    print "clever == stupid:", clever_result == stupid_result

    minz = z_encode(3, 5)
    maxz = z_encode(5, 10)

    print "stupid LITMAX 58 =", stupid_litmax(minz, maxz, 58)
    print "stupid BIGMIN 58 =", stupid_bigmin(minz, maxz, 58)

    print "clever LITMAX 58 =", clever_litmax(minz, maxz, 58)
    print "clever BIGMIN 58 =", clever_bigmin(minz, maxz, 58)

    litmax_diff = [n for n in nodes
        if stupid_litmax(minz, maxz, n.zcode) !=
           clever_litmax(minz, maxz, n.zcode)]

    bigmin_diff = [n for n in nodes
        if stupid_bigmin(minz, maxz, n.zcode) !=
           clever_bigmin(minz, maxz, n.zcode)]

    print "litmax diff:", litmax_diff
    print "bigmin diff:", bigmin_diff

if __name__ == "__main__":
    main()