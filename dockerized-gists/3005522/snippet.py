#!/usr/bin/python
# -*- coding: utf-8 -*-

def powerset(s):
  return [[s[j] for j in xrange(len(s)) if (i&(1<<j))] for i in xrange(1<<len(s))]

s = ['a','b','c','d']
print powerset(s)