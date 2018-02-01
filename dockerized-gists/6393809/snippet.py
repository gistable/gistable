import unittest

from mock import call, patch


class PatcherTestCase(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('some_module.some_object')
        self.mock_object = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def assertMockCallsEqual(self, *args):
      self.assertEqual(self.mock_object.call_args_list, list(args))

    def test_something(self):
      # Do something that impacts mock object
      pass

      # Make assertions about mock object state
      self.assertMockCallsEqual(
        call('arg_1_value', 'arg_2_value', 'arg_3_value'),  # call 1
        call('arg_1_value', 'arg_2_value', 'arg_3_value'),  # call 2
      )