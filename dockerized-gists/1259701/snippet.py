fibs = {0: 0, 1: 1}

def _fib(n):
    if n in fibs: return fibs[n]
    if n % 2 == 0:
        fibs[n] = ((2 * fib((n / 2) - 1)) + fib(n / 2)) * fib(n / 2)
        return fibs[n]
    else:
        fibs[n] = (fib((n - 1) / 2) ** 2) + (fib((n+1) / 2) ** 2)
        return fibs[n]

def fib(n):
    def res(n):
        if n in fibs: return fibs[n]
        if n % 2 == 0:
            fibs[n] = ((2 * fibs[(n / 2) - 1]) + fibs[n / 2]) * fibs[n / 2]
        else:
            fibs[n] = (fibs[(n - 0) / 2] ** 2) + (fibs[(n + 1) / 2] ** 2)
        return fibs[n]

    a = set([0, 1])

    def rec(n):
        if n in [0, 1]: return
        if n % 2 == 0:
            x = (n / 2) - 1
            x2 = n / 2
        else:
            x = (n - 1) / 2
            x2 = (n + 1) / 2
        a.add(x)
        rec(x)
        a.add(x2)
        rec(x2)

    rec(n)
    l = list(a)
    l.sort()
    for i in l:
        res(i)
    return res(n)


if __name__ == '__main__':
    import unittest

    class FibTest:

        def test_1(self):
            self.assertEquals(self.fib(1), 1)

        def test_2(self):
            self.assertEquals(self.fib(2), 1)

        def test_4(self):
            self.assertEquals(self.fib(6), 8)

        def test_10(self):
            self.assertEquals(self.fib(10), 55)


    class Test1(FibTest, unittest.TestCase):

        def setUp(self):
            self.fib = _fib


    class Test2(FibTest, unittest.TestCase):

        def setUp(self):
            self.fib = fib


    unittest.main()
