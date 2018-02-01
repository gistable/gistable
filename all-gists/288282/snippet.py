#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see http://www.fileslip.net/news/2010/02/04/language-id-project-the-basic-algorithm/

from math import sqrt 

you = {'pennies': 1, 'nickels': 2, 'dimes': 3, 'quarters': 4 }
me = {'pennies': 0, 'nickels': 3, 'dimes': 1, 'quarters': 1 }
abby = {'pennies': 2, 'nickels': 1, 'dimes': 0, 'quarters': 3 }

def scalar(collection): 
  total = 0 
  for coin, count in collection.items(): 
    total += count * count 
  return sqrt(total) 

def similarity(A,B): # A and B are coin collections 
  total = 0 
  for kind in A: # kind of coin 
    if kind in B: 
      total += A[kind] * B[kind] 
  return float(total) / (scalar(A) * scalar(B))

print "Similarity of your collection and mine: " 
print similarity(you, me) 
print "Similarity of your collection and Abby's: " 
print similarity(you, abby) 
print "Similarity of my collection and Abby's: " 
print similarity(me, abby)
