"""Splay tree
Logan Ingalls <log@plutor.org>
Sept 3, 2012

Note that I only implemented insert and find. Delete is trivial,
and isn't the interesting part of splay trees. Some of these
algorithms would be simpler, but I chose to do this without parent
links from the tree nodes.

Example output on my desktop computer:

Building trees
Done building
Searched for 20 items 20000x in splay tree: 4.1 sec
Searched for 20 items 20000x in binary tree: 11.1 sec
"""

from random import shuffle
import time

class BinaryTreeNode:
    """A node in a binary tree. Each node has a val attribute,
    as well as left and right descendents. No parent links because
    I'm a masochist."""
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

    def __str__(self):
        return ("node[%s]" % self.val)

class BinaryTree:
    """A basic binary tree."""
    def __init__(self):
        self.root = None

    def insert(self, val, parent=None):
        """Insert a new value in the tree. Takes one argument
        (the value to insert). Recursive binary search."""
        if (parent == None):
            parent = self.root
        if (parent == None):
            # root is null, make this the new root, done
            self.root = BinaryTreeNode(val)
            return
        elif (val < parent.val):
            if (parent.left == None):
                # insert to the left of the parent
                parent.left = BinaryTreeNode(val)
                return
            else:
                # search under the left
                self.insert(val, parent.left)
        else:
            if (parent.right == None):
                # insert to the right of the parent
                parent.right = BinaryTreeNode(val)
                return
            else:
                # search under the right
                self.insert(val, parent.right)

    def find(self, val, node=None):
        """Find if a value is in the tree. Takes one argument
        (the value to find). If the value is in the tree, returns
        the node object. Otherwise returns None."""
        if (node == None):
            node = self.root
        if (node == None):
            # obviously it's not in an empty tree
            return None
        elif (val == node.val):
            return node
        elif (val < node.val):
            # Search left
            if (node.left != None):
                leftrv = self.find(val, node.left)
                if leftrv != None:
                    return leftrv
        elif (val > node.val):
            if (node.right != None):
                rightrv = self.find(val, node.right)
                if rightrv != None:
                    return rightrv
        return None

class SplayTree(BinaryTree):
    """Implementation of a splay tree. Splay trees are self-organizing.
    They look identical to binary trees, but when nodes are found, they
    are moved towards the root (one or two levels closer). Still
    O(lg n), but a shallower search on average when not all values are
    searched for equally."""
    def find(self, val, node=None, p=None, g=None, gg=None):
        """Find if a value is in the tree. Takes one argument
        (the value to find). If the value is in the tree, returns
        the node object. Otherwise returns None."""
        if (node == None):
            node = self.root
        if (node == None):
            # obviously it's not in an empty tree
            return None
        elif (val == node.val):
            # If it's found, we need to move things around
            if (p != None):
                if (g == None):
                    # Zig: swap node with its parent
                    self.rotateup(node, p, g)
                elif ((g.left == p and p.left == node) or
                      (g.right == p and p.right == node)):
                    # Zig-zig: swap parent with grandparent
                    self.rotateup(p, g, gg)
                    # Then swap node with parent
                    self.rotateup(node, p, gg)
                else:
                    # Zig-zag: swap node with parent
                    self.rotateup(node, p, g)
                    # Then swap node with grandparent
                    self.rotateup(node, g, gg)
            return node
        elif (val < node.val):
            # Search left
            if (node.left != None):
                leftrv = self.find(val, node.left, node, p, g)
                if leftrv != None:
                    return leftrv
        elif (val > node.val):
            if (node.right != None):
                rightrv = self.find(val, node.right, node, p, g)
                if rightrv != None:
                    return rightrv
        return None

    def rotateup(self, node, parent, gp=None):
        """Swap a node with its parent, keeping all child nodes
        (and grandparent node) in order."""
        if node == parent.left: 
            parent.left = node.right
            node.right = parent
            if (self.root == parent):
                self.root = node
        elif node == parent.right:
            parent.right = node.left
            node.left = parent
            if (self.root == parent):
                self.root = node
        else:
            print("This is impossible")

        if (gp != None):
            if (gp.right == parent):
                gp.right = node
            elif (gp.left == parent):
                gp.left = node

def test_splay_tree(treesize=100000, iters=20000):
    """Just a simple test harness to demonstrate the speed of
    splay trees when a few items are searched for very frequently."""
    # Build a binary tree and a splay tree
    print("Building trees")
    bintree = BinaryTree()
    spltree = SplayTree()
    x = [i for i in range(0, treesize)]
    shuffle(x)
    for n in x:
        bintree.insert(n)
        spltree.insert(n)
    print("Done building")
    searches = x[-20:]

    # Search the splay tree 1000 times
    t1 = time.time()
    for i in range(0, iters):
        for n in searches:
            node = spltree.find(n)
            if (node == None):
                print("ERROR: %d" % n)
    t2 = time.time()
    print("Searched for 20 items %dx in splay tree: %.1f sec" % (iters, t2-t1))

    # Search the binary tree 1000 times
    t1 = time.time()
    for i in range(0, iters):
        for n in searches:
            node = bintree.find(n)
            if (node == None):
                print("ERROR: %d" % n)
    t2 = time.time()
    print("Searched for 20 items %dx in binary tree: %.1f sec" % (iters, t2-t1))

test_splay_tree()
