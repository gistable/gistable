#!/usr/bin/python
# -*- coding: utf-8 -*-

def f(x):
  """
  returns x * x
  >>> f(5)
  25
  >>> f(-3)
  9
  """
  return x * x

if __name__ == "__main__":
  from doctest import testmod
  testmod() # without parameter: test the current module
