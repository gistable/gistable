def _chunker(it):
    while True:
        yield (it.next(), it.next())

def chunker(seq):
    return map(list, _chunker(iter(seq)))


import unittest

class ChunkerTest(unittest.TestCase):
    def test_balance(self):
        result = chunker([1, 2, 3, 4, 5, 6])
        expected = [[1, 2], [3, 4], [5, 6]]
        self.assertEqual(result, expected)

    def test_unbalance(self):
        result = chunker([1, 2, 3, 4, 5])
        expected = [[1, 2], [3, 4]]
        self.assertEqual(result, expected)

    def test_empty(self):
        result = chunker([])
        expected = []
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
