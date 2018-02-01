import random


# A demonstration of traversing a binary search tree in order.
# See the traverse function for all the action.


# Generic binary tree class

class Tree:

    def __init__(self, value):
        self._left = None
        self._right = None
        self._value = value

    def setLeftChild(self, child):
        self._left = child

    def setRightChild(self, child):
        self._right = child

    def getLeftChild(self):
        return self._left

    def getRightChild(self):
        return self._right

    def getValue(self):
        return self._value


# Traverse a binary search tree -- if we're expecting very deep
# trees, an iterative rather than recursive method would be safer;
# or consider Stackless Python, although it's not truly stackless
# (http://www.stackless.com/pipermail/stackless/2012-October/005461.html)

# "yield" allows us to use the function in a generator (see below)

def traverse(bst):
    left = bst.getLeftChild()
    if left is not None:
        for subtree in traverse(left):
            yield subtree
    yield bst.getValue()
    right = bst.getRightChild()
    if right is not None:
        for subtree in traverse(right):
            yield subtree


# Helper method for adding a new value

def add(bst, value):
    # Lower values to the left
    if value < bst.getValue():
        left = bst.getLeftChild()
        if left is None:
            bst.setLeftChild(Tree(value))
        else:
            add(left, value)
    # Higher values to the right
    elif value > bst.getValue():
        right = bst.getRightChild()
        if right is None:
            bst.setRightChild(Tree(value))
        else:
            add(right, value)
    # If value == bst.getValue(), take no action (it's a duplicate)


# Generate some test data

bst = Tree(50)
for i in range(100):
    value = random.randint(0, 100)
    print "Adding value ", value
    add(bst, value)

print "In order: ", list(x for x in traverse(bst))




