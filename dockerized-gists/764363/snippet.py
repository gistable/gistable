# modified from http://bit.ly/dEyw03

import unittest

class TestMyGoods(unittest.TestCase):
    pass

def create_dynamic_method(pair):
    """just don't include `test` in the function name here, nose will try to
    run it"""
    def dynamic_test_method(self):
        """this function name doesn't matter much, it can start with `test`,
        but we're going to rename it dynamically below"""
        self.assertEqual(pair, pair) # this is our actual assertion
    return dynamic_test_method

for k, pair in enumerate(xrange(12)):
    dynamic_method = create_dynamic_method(pair)
    dynamic_method.__name__ = 'test_{0}'.format(k)
    dynamic_method.__doc__ = 'my super great name {0}'.format(k)
    setattr(TestMyGoods, dynamic_method.__name__, dynamic_method)
    # remove the last test name from the current namespace, 
    # so nose doesn't run it
    del dynamic_method

if __name__ == '__main__':
    unittest.main()