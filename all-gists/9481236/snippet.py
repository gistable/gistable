import unittest

from solution import is_happy, happy_primes

class TestHappy(unittest.TestCase):
    def test_is_happy7(self):
        self.assertEqual(is_happy(7), True)

    def test_is_happy10(self):
        self.assertEqual(is_happy(10), True)

    def test_is_happ11(self):
        self.assertEqual(is_happy(11), False)

    def test_is_happy97(self):
        self.assertEqual(is_happy(97), True)


    def test_is_happy368(self):
        self.assertEqual(is_happy(368), True)

    def test_is_happy380(self):
        self.assertEqual(is_happy(380), False)

    def test_happy_primes_63(self):
        self.assertEqual(happy_primes(range(63,100)), [79,97])

    def test_happy_primes_135(self):
        self.assertEqual(happy_primes(range(135, 250)), [139, 167, 193, 239])

if __name__ == '__main__':
    unittest.main()
