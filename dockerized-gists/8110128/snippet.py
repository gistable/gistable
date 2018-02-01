#!/usr/bin/env python
#coding: utf-8

# Demo of Python exception

import unittest


def try_except(L, index):
    result = 0
    try:
        L[index] += 1
        result += 1
    except IndexError:
        result += 2
    return result


def try_raise():
    try:
        raise IndexError
        return 0
    except IndexError:
        return 1
    return 2


class SelfException(Exception):
    pass


def selfexception_tricker():
    try:
        raise SelfException
        return 0
    except SelfException:
        return 1
    return 2


def try_finally(L, index):
    result = 0
    try:
        L[index] += 1
        result += 1
    except Exception:
        pass
    finally:
        result += 2
    return result


class TestException(unittest.TestCase):
    def setUp(self):
        self.tlist = [1, 2, 3]

    def testTryFinally(self):
        self.assertEqual(
                try_finally(self.tlist, 1),
                3)
        self.assertEqual(
                try_finally(self.tlist, 4),
                2)

    def testTryExcept(self):
        self.assertEqual(
                try_except(self.tlist, 1),
                1)
        self.assertEqual(
                try_except(self.tlist, 4),
                2)

    def testTryRaise(self):
        self.assertEqual(
                try_raise(),
                1)

    def testSelfException(self):
        self.assertEqual(
                selfexception_tricker(),
                1)


if __name__ == '__main__':
    unittest.main()