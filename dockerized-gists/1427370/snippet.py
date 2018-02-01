#!/usr/bin/env python3

from itertools import cycle


def chksum(val):
  def tonum(v):
    if len(v) == 1:
      if v == '<':
        return 0
      c = ord(v)
      if ord('0') <= c <= ord('9'):
        return c - ord('0')
      if ord('A') <= c <= ord('Z'):
        return c - ord('A') + 10
    raise ValueError('Invalid character')

  val = str(val)
  return sum(map(lambda p: p[0]*p[1],zip(map(tonum, val), cycle([7, 3, 1])))) % 10
