# -*- coding: utf-8 -*-
import unittest

operators = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b
}

def polish_eval(expression):
    elements = expression.split()
    pile = []
    while elements:
        e = elements.pop(0)
        if e in operators:
            b = pile.pop()
            a = pile.pop()
            pile.append(operators[e](a, b))
        else:
            pile.append(int(e))
    return pile[0]


class TestPolish(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(3, polish_eval('1  2    +'))
        self.assertEqual(4, polish_eval('2 2 +'))
        self.assertEqual(1, polish_eval('-4 5 +'))

    def test_soustraction(self):
        self.assertEqual(1, polish_eval('3 2 -'))
        self.assertEqual(4, polish_eval('3 2 1 - +'))

    def test_acceptance(self):
        self.assertEqual(2, polish_eval('4 2 5 * + 1 3 2 * + /'))

    def test_acceptance2(self):
        self.assertEqual(14, polish_eval('5 1 2 + 4 * 3 - +'))
