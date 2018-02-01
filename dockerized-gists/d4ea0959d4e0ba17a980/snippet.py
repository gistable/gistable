import shutil, tempfile
from os import path
import unittest

class TestExample(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_something(self):
        # Create a file in the temporary directory
        f = open(path.join(self.test_dir, 'test.txt'), 'w')
        # Write something to it
        f.write('The owls are not what they seem')
        # Reopen the file and check if what we read back is the same
        f = open(path.join(self.test_dir, 'test.txt'))
        self.assertEqual(f.read(), 'The owls are not what they seem')

if __name__ == '__main__':
    unittest.main
