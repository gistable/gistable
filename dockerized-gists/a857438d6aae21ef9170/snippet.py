#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

def term(i):
  # n = 4.0/(2*i + 1)
  # return -n if i & 1 else n
  return (-1)**i * 4.0/(2*i + 1)

def pi(n):
  """Pi up to n terms."""
  return sum(map(term, xrange(n)))
