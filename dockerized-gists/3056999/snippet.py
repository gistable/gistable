""" This is a simple gist to show how to mock
private methods. I've got lots of questions
regarding this topic. Most people seems confused.

Hope it helps.
"""


import unittest
import mock


class Car:
    def __private(self):
        return 1

    def no_private(self):
        return self.__private()


class CarTest(unittest.TestCase):

    def test_exception_raises(self):
        c = Car()
        with self.assertRaises(AttributeError):
            c.__private()

    def test_car_works(self):
        c = Car()
        self.assertEqual(c.no_private(), 1)

    def test_mock_private(self):
        c = Car()
        with mock.patch.object(c, '_Car__private', return_value=3) as method:
            c.no_private()
            method.assert_called_once_with()

if __name__ == "__main__":
    unittest.main()