#!/usr/local/bin/python3

class AVLTree:
    def __init__(self, data):
        self.data = data
        self.lhs = None
        self.rhs = None

    def insert(self, data):
        if data == self.data:
            return
        self._insert(data, 'lhs' if data < self.data else 'rhs')
        self._rebalance()

    def _insert(self, data, side):
        child = getattr(self, side)
        if child:
            child.insert(data)
        else:
            setattr(self, side, AVLTree(data))

    def _rebalance(self):
        balance = self._height(self.lhs) - self._height(self.rhs)
        if balance > 1:
            llheight = self._height(self.lhs.lhs)
            lrheight = self._height(self.lhs.rhs)
            if lrheight > llheight:
                self.lhs._rotate_left()
            self._rotate_right()
        elif balance < -1:
            rlheight = self._height(self.rhs.lhs)
            rrheight = self._height(self.rhs.rhs)
            if rlheight > rrheight:
                self.rhs._rotate_right()
            self._rotate_left()

    def _height(self, node):
        if not node:
            return 0
        else:
            return 1 + max(self._height(node.lhs), self._height(node.rhs))

    def _rotate_left(self):
        cog, A, B, C = self.rhs, self.lhs, self.rhs.lhs, self.rhs.rhs
        self.lhs, self.data, cog.data = cog, cog.data, self.data
        self.rhs, cog.lhs, cog.rhs = C, A, B

    def _rotate_right(self):
        cog, B, C, D = self.lhs, self.lhs.lhs, self.lhs.rhs, self.rhs
        self.rhs, self.data, cog.data = cog, cog.data, self.data
        self.lhs, cog.lhs, cog.rhs = B, C, D

    def rigid(self):
        ok = abs(self._height(self.lhs) - self._height(self.rhs)) <= 1
        return ok and \
                self.lhs.rigid() if self.lhs else True and \
                self.rhs.rigid() if self.rhs else True

    def show(self, indent = 0):
        if self.lhs:
            self.lhs.show(indent + 1)
        print(' ' * (2 * indent) + '> ' + str(self.data))
        if self.rhs:
            self.rhs.show(indent + 1)

if __name__ == '__main__':
    import random
    t = AVLTree(0)
    for x in range(100):
        t.insert(random.random())
    assert t.rigid()
    t.show()

    dt = AVLTree(0)
    for x in range(100):
        t.insert(x)
    assert t.rigid()
    t.show()