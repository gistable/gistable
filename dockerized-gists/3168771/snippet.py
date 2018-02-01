#!/usr/bin/env python2.7

import random
import subprocess


class Node(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self._left = None
        self._right = None

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value
    

class BalancedTree(object):
    def __init__(self, key_func=lambda x: id(x)):
        self._root = None
        self._key_func = key_func

    def _insert(self, node, subtree):
        if node.key <= subtree.key:
            if subtree.left is None:
                subtree.left = node
            else:
                self._insert(node, subtree.left)
        else:
            if subtree.right is None:
                subtree.right = node
            else:
                self._insert(node, subtree.right)

    def insert(self, value):
        node = Node(self._key_func(value), value)
        if self._root is None:
            self._root = node
        else:
            self._insert(node, self._root)

    def _left_to_right(self, subtree):
        if subtree is None:
            return

        for i in self._left_to_right(subtree.left):
            yield i

        yield subtree.value

        for i in self._left_to_right(subtree.right):
            yield i

    def _balance(self, subtree, element_list):
        if not element_list:
            return
        right_list_length = len(element_list)/2
        value = element_list[right_list_length]
        node = Node(self._key_func(value), value)
        self._insert(node, subtree)
        self._balance(node, element_list[:right_list_length])
        self._balance(node, element_list[right_list_length+1:])

    def balance(self):
        sorted_elements = list(self._left_to_right(self._root))

        if not sorted_elements:
            self._root = None
            return

        right_list_length = len(sorted_elements)/2
        value = sorted_elements[right_list_length]
        node = Node(self._key_func(value), value)
        self._root = node
        self._balance(node, sorted_elements[:right_list_length])
        self._balance(node, sorted_elements[right_list_length+1:])

    def _get_dot(self, node):
        if node.left is not None:
            yield "\t%s -> %s;" % (node.key, node.left.key)
            for i in self._get_dot(node.left):
                yield i
        elif node.right is not None:
            r = random.randint(0, 1e9)
            yield "\tnull%s [shape=point];" % r
            yield "\t%s -> null%s;" % (node.key, r)
        if node.right is not None:
            yield "\t%s -> %s;" % (node.key, node.right.key)
            for i in self._get_dot(node.right):
                yield i
        elif node.left is not None:
            r = random.randint(0, 1e9)
            yield "\tnull%s [shape=point];" % r
            yield "\t%s -> null%s;" % (node.key, r)

    def get_dot(self):
        return "digraph G{\n%s}" % ("" if self._root is None else (
            "\t%s;\n%s\n" % (
                self._root.key,
                "\n".join(self._get_dot(self._root))
            )
        ))


def _prepare_data():
    return (0, 1, 2, 3, 4, 5, 6, 7)


if __name__ == "__main__":
    d = _prepare_data()
    tree = BalancedTree(lambda x: x)
    for data in d:
        tree.insert(data)

    tree.balance()

    d = tree.get_dot()

    t = subprocess.Popen(["dot", "-Tpng"], stdin=subprocess.PIPE)
    t.communicate(d)
