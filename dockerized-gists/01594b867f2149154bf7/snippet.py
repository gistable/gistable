# -*- coding: utf-8 -*-

import unittest


index = {}


class tree(object):

    def __init__(self, name=None):
        self.value = name
        self.left = None
        self.right = None

    def add(self, parent, child):

        p = self.find(parent)

        n = tree(child)

        if p and not p.left:
            p.left = n
        elif p and not p.right:
            p.right = n
        elif p:
            raise TypeError("No more child appowed")
        else:
            self.value = parent
            self.left = n

        index[child] = n


    def find(self, parent):

        if self.value == parent:
            return self
        
        """
        if self.right:
            c = self.right.find(parent)
            if c: return c

        if self.left:
            c = self.left.find(parent)
            if c: return c
        return None
        """

        return index.get(parent)


    def print_tree(self, indent=0):
    
        print ' ' * indent + self.value

        indent += 1

        if self.right:
            self.right.print_tree(indent)
        if self.left:
            self.left.print_tree(indent)


    def __repr__(self, indent=0):

        ret = ' ' * indent + self.value

        indent += 1

        if self.right:
            ret += '\n' + self.right.__repr__(indent)
        if self.left:
            ret += '\n' + self.left.__repr__(indent)

        return ret



class TestTree(unittest.TestCase):

    def setUp(self):

        self.tree = tree()


    def test_onelevel(self):

        self.tree.add('Jon', 'Elen')

        self.assertEqual(str(self.tree), "Jon\n Elen")


    def test_twolevel(self):

        self.tree.add('Jon', 'Elen')
        self.tree.add('Elen', 'Rachel')
        self.tree.add('Elen', 'Tomas')

        self.assertEqual(str(self.tree), "Jon\n Elen\n  Tomas\n  Rachel")


    def test_errortwolevel(self):

        self.tree.add('Jon', 'Elen')
        self.tree.add('Elen', 'Rachel')
        self.tree.add('Elen', 'Tomas')
        try:
            self.tree.add('Elen', 'Paul')
            self.assertTrue(False)
        except TypeError, e:
            print e
            self.assertTrue(True)

        

"""
n = tree()
n.add('Jon', 'Elen')
n.add('Jon', 'Alan')
n.add('Alan', 'Paul')
n.add('Elen', 'Rachel')
n.add('Elen', 'Tomas')

print n
"""

if __name__ == '__main__':

    unittest.main()
