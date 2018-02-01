import unittest

from solution import is_happy, happy_primes


class TestHappyNumbers(unittest.TestCase):

    def test_is_happy_3(self):
        self.assertEqual(is_happy(3), False)

    def test_is_happy_10(self):
        self.assertEqual(is_happy(10), True)

    def test_is_happy_negative(self):
        self.assertEqual(is_happy(-5), False)

    def test_is_happy_zero(self):
        self.assertEqual(is_happy(0), False)

    def test_happy_primes_from_negative(self):
        self.assertEqual(happy_primes(range(-5, 25)), [7, 13, 19, 23])

    def test_happy_primes_zero(self):
        self.assertEqual(happy_primes(range(0)), [])

    def test_happy_primes_negative(self):
        self.assertEqual(happy_primes(range(-5)), [])

    def test_happy_primes_range(self):
        self.assertEqual(happy_primes(range(100)), [7, 13, 19, 23, 31, 79, 97])

if __name__ == '__main__':
    unittest.main()