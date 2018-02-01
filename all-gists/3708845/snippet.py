#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 20:48:25 2012

T9 Message to cell phone numbers to be pressed

Problem description:
  http://dojopuzzles.com/problemas/exibe/escrevendo-no-celular/

@author: Danilo de Jesus da Silva Bellini
"""

import unittest
import operator
import string
import itertools as it


def cel(msg):
  letters_upper = string.ascii_uppercase # Thanks Luciano Ramalho! =)
  letters_lower = string.ascii_lowercase + " "
  digits_from_2 = string.digits[2:]

  # dig3 = [["2", "22", "222"], ["3", "33", "333"], ... ["9", "99", "999"]]
  dig3 = [[digit * length for length in [1, 2, 3]]
                          for digit in digits_from_2]

  # Flatten dig3
  dig3flat = reduce(operator.concat, dig3)

  # Now we have all the digits, in order:
  digits = sorted(dig3flat + ["7777", "9999"]) + ["0"]

  # Mapping (dict) between letters and digits.
  keys = {k:v for k, v in it.chain(it.izip(letters_upper, digits),
                                   it.izip(letters_lower, digits))}

  # Apply the mapping for each char in the message, but store as a list
  strings = [keys[letter] for letter in msg]

  # Insert the separator when needed
  corrected = [("_" if last[0] == new[0] else "") + new
               for last, new in it.izip([" "] + strings, strings)]

  # Finished! This code can be easily replaced by an one-liner, just with
  # a "copy and paste" process avoiding the name "corrected" below and so on
  # in the return until no name is left but "msg", and this whole function
  # could then be a lambda, though not that expressive...
  return "".join(corrected)


class CelTester(unittest.TestCase):

  def test_empty(self):
    self.assertEqual(cel(""), "")

  def test_a(self):
    self.assertEqual(cel("A"), "2")

  def test_b(self):
    self.assertEqual(cel("B"), "22")

  def test_c(self):
    self.assertEqual(cel("C"), "222")

  def test_d(self):
    self.assertEqual(cel("D"), "3")

  def test_ad(self):
    self.assertEqual(cel("AD"), "23")

  def test_ac(self):
    self.assertEqual(cel("AC"), "2_222")

  def test_ab(self):
    self.assertEqual(cel("AB"), "2_22")

  def test_danilo(self):
    self.assertEqual(cel("DANILO"), "3266444555666")

  def test_sempre_acesso_o_dojo_puzzles(self):
    self.assertEqual(cel("SEMPRE ACESSO O DOJO PUZZLES"),
                     "77773367_7773302_222337777_77776660"
                     "66603666566607889999_9999555337777")

  def test_sempre_acesso_o_dojopuzzles(self):
    self.assertEqual(cel("SEMPRE ACESSO O DOJOPUZZLES"),
                     "77773367_7773302_222337777_77776660"
                     "6660366656667889999_9999555337777")

  def test_sempre_acesso_o_dojopuzzles_lower_upper_mixed(self):
    self.assertEqual(cel("SemPrE ACesSO o dOJOPUzZLES"),
                     "77773367_7773302_222337777_77776660"
                     "6660366656667889999_9999555337777")


if __name__ == "__main__":
  unittest.main()