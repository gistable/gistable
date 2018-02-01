"""Run PEP8 on all Python files in this directory and subdirectories as part of the tests."""

__author__ = 'Christopher Swenson'
__email__ = 'chris@caswenson.com'
__license__ = 'CC0 http://creativecommons.org/publicdomain/zero/1.0/'

import os
import os.path
import unittest

import pep8

# ignore stuff in virtualenvs or version control directories
ignore_patterns = ('.svn', 'bin', 'lib' + os.sep + 'python')


def ignore(dir):
  """Should the directory be ignored?"""
  for pattern in ignore_patterns:
    if pattern in dir:
      return True
  return False


class TestPep8(unittest.TestCase):
  """Run PEP8 on all files in this directory and subdirectories."""
  def test_pep8(self):
    style = pep8.StyleGuide(quiet=True)
    style.options.ignore += ('E111',)  # 4-spacing is just too much
    style.options.max_line_length = 100  # because it isn't 1928 anymore

    errors = 0
    for root, _, files in os.walk('.'):
      if ignore(root):
        continue

      python_files = [f for f in files if f.endswith('.py')]
      errors += style.check_files(python_files).total_errors

    self.assertEqual(errors, 0, 'PEP8 style errors: %d' % errors)
