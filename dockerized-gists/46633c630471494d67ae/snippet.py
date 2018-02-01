#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License v2 as published by
#the Free Software Foundation.

"""Algorithmic pseudo-random permutations for large sequences.

Module to generate random, arbitrarily large permutations. Random permutations
can be generated in Python with random.shuffle or numpy.random.shuffle:

  import random

  indexes = range(100)
  random.shuffle(indexes)

  import numpy
  import numpy.random

  indexes = numpy.arange(100)
  numpy.random.shuffle(indexes)

However, this is restricted to permutations that hold on main memory.

Sometimes, it may be convenient to use very large random permutations. I wrote
the original version of this code several years ago, in MATLAB, when I had a very
large sequence of identifiers whose length was not a power of two, and needed to
generate a random permutation of the sequence.

This module provides two classes to implement such long permutations:
LongPermutation and SPNetwork, with a common interface:

* attribute numvalues: length of the permutation

* method permValue: return the value in the permutation sequence for the given index

* method permIndex: give a value of the permutation sequence, return its index (permValue(a)==b  <==>  permIndex(b)==a)

The class LongPermutation defines permutations of any length. The class
SPNetwork defines permutations whose length is a power of two.



"""
import math as m
import random as r

from collections import namedtuple

######################################################
#MAIN CLASSES
######################################################

class LongPermutation:
  """Define a permutation of very large size"""
  def __init__(self, numvalues, nstages=None):
    """for a given number of values, define a permutation. nstages is the number of stages of the underlying SPNetwork"""
    self.numvalues = long(numvalues)
    self.nbits     = int(m.ceil(m.log(float(numvalues), 2)))
    #if numvalues is too big to be stored in a float with enough precision (around 2e15), we add a bit to avoid problems related to losing resolution
    if self.numvalues>2e15:
      self.nbits  += 1
    self.spn       = SPNetwork(self.nbits, nstages)
  
  def cyclewalking(self, value, spnfun):
    """Internal function.
    
    Uses algorithm for FPE (See http://en.wikipedia.org/wiki/Format-preserving_encryption#FPE_from_cycle_walking ).
    We use it to translate a permutation of custom size self.numvalues from/to a permutation of size 2**nbits (the SPNetwork)"""
    checknum(value, self.numvalues, "LongPermutation")
    cipher = value
    goon   = True
    while goon:
      cipher = spnfun(cipher)
      goon   = cipher>=self.numvalues
    return cipher
  
  def permValue(self, index):
    """return the index-th element of the permutation."""
    return self.cyclewalking(index, self.spn.permValue)

  def permIndex(self, value):
    """inverse operation of value(): for a given value, return its index. index(value(a))==a"""
    return self.cyclewalking(value, self.spn.permIndex)

  
class SPNetwork:
  """a substitution-permutation network intended to compute arbitrarily large permutations with 2**nbits values.
  
  This is actually a mathematical construction from Crypto 101"""
  
  def __init__(self, nbits, nstages=None):
    """Constructor for SPNetwork.
    
    nbits is the number of bits of the numbers to encrypt/decrypt.
    
    nstages is the number of stages of the network. The more stages, the better the randomness of the permutation (up to a point, of course)"""
    if nstages is None:
      nstages      = 15
    self.nbits   = int(nbits)
    self.nstages = nstages
    self.numvalues  = 1<<nbits
    rest = nbits % 8
    if rest>0:
      self.lastshift = 8-(nbits%8)
    else:
      self.lastshift = 0
    self.stages  = [makeSPStage(nbits) for _ in xrange(nstages)]
  
  def applyPBox(self, value, stage, mode):
    """apply the pbox to encrypt/decrypt. A p-box is a permutation of the bits in the value"""
    newvalue = long(0)
    pbox = stage.pbox.__getattribute__(mode)
    for k in xrange(self.nbits):
      if value & (1<<k):
        newvalue |= 1<<pbox[k]
    return newvalue
    
  def applySBoxes(self, value, stage, mode):
    """apply the sboxes to encrypt/decrypt. Each s-box is a lookup table applied to a segment of the value"""
    #each sbox is applied to a chunk of the bit sequence
    startbit         = self.nbits
    newvalue         = long(0)
    for sbox, size in zip(stage.sboxes, stage.sizebybox):
      sbox           = sbox.__getattribute__(mode)          #select mode
      newstart       = startbit-size
      selected       = selectbitrange(newstart, startbit)   #range of bits to apply the sbox
      v              = (value & selected) >> newstart       #bring the bits to the right
      v              = sbox[v]                              #apply the sbox
      newvalue      |= selected & (v << newstart)           #put the result in its place
      startbit       = newstart                             #update index vars

    return newvalue
  
  def permValue(self, index):
    """encrypt an index, i.e., compute the index-th element of the permutation of 2**nbits"""
    checknum(index, self.numvalues, "SPNetwork")
    value    = long(index)
    for stage in self.stages:
      value  = self.applySBoxes(value, stage, 'encrypt')
      value  = self.applyPBox  (value, stage, 'encrypt')
      value ^= stage.key
    return value
  
  def permIndex(self, value):
    """inverse of encrypt, i.e., compute the index in the permutation for the given value. permValue(a)==b  <==>  permIndex(b)==a"""
    checknum(value, self.numvalues, "SPNetwork")
    index    = long(value)
    #apply operations in reverse order w.r.t permValue()
    for stage in reversed(self.stages):
      index ^= stage.key
      index  = self.applyPBox  (index, stage, 'decrypt')
      index  = self.applySBoxes(index, stage, 'decrypt')
    return index
      
######################################################
#HELPER FUNCTIONS
######################################################

def selectbitrange(start, stop):
  value = long(0)
  for k in xrange(start, stop):
    value |= 1<<k
  return value

def checknum(value, numvalues, name):
  """input sanity checks"""
  if value<0:
    raise ValueError(name+' works with positive numbers')
  if value>=numvalues:
    raise ValueError('number out of range for this '+name)

#building blocks for SPNetwork
Box     = namedtuple('Box', ['encrypt', 'decrypt'])
SPStage = namedtuple('SPStage', ['key', 'sboxes', 'sizebybox', 'pbox'])

def makeSPStage(nbits):
  """a stage of a SP network has a random key of nbits, a list of 8-bit random sboxes (the last one may be smaller), and a random pbox of nbits"""
  numsboxes  = int(m.ceil(nbits/8.0))
  rest       = nbits % 8
  sizebybox  = [8]*numsboxes
  if rest>0:
    sizebybox[-1] = rest
  key        = r.getrandbits(nbits)
  pbox       = makebox(nbits)
  sboxes     = [makebox(1<<v) for v in sizebybox] 
  return SPStage(key=key, sboxes=sboxes, sizebybox=sizebybox, pbox=pbox)
 
def makebox(size):
  """define a box as a random permutation, works both for sboxes and pboxes"""
  perm = range(size)
  r.shuffle(perm)
  idxs = argsort(perm)
  return Box(encrypt=perm, decrypt=idxs)

def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)

######################################################
#EXAMPLES
######################################################

def EXAMPLE1(length=20, nstages=15):
  p = LongPermutation(length, nstages=nstages)
  print "TESTING all indexes of LongPermutation with %d values" % length
  testPermutationAll(p, show=True)
  print "NO EXCEPTIONS, SO EVERYTHING IS OK"
  print "\nTESTING THE UNDERLYING SPNetwork"
  testPermutationAll(p.spn, show=True)
  print "NO EXCEPTIONS, SO EVERYTHING IS OK"

def EXAMPLE2(length=123123123123123123123123123123123123123123123, numFirstIndexes=20, nstages=15):
  p = LongPermutation(length, nstages=nstages)
  indexes = xrange(numFirstIndexes)
  print "TESTING %d first indexes of LongPermutation with %d values" % (numFirstIndexes, length)
  testPermutationSelection(p, indexes, show=True)
  print "NO EXCEPTIONS, SO EVERYTHING IS OK"
  print "\nTESTING THE UNDERLYING SPNetwork"
  testPermutationSelection(p.spn, indexes, show=True)
  print "NO EXCEPTIONS, SO EVERYTHING IS OK"

def EXAMPLE3(length=1000, nstages=15):
  p = LongPermutation(length, nstages=nstages)
  plotPermutation(p)

######################################################
#TEST DEFINITIONS
######################################################

def plotPermutation(permutator):
  import matplotlib.pyplot as plt
  import numpy as n
  x = n.arange(permutator.numvalues)
  y = n.array([permutator.permValue(a) for a in x])
  plt.figure()
  plt.plot(x,y,'.')
  plt.title('Permutation')
  plt.figure()
  x = n.random.random((permutator.numvalues,))
  y = n.random.random((permutator.numvalues,))
  plt.plot(x,y,'.')
  plt.title('random values')
  plt.show()

def testPermutationSelection(permutator, indexes, show=False):
  """test a sequence of indexes for a permutator object (use this to test networks with large nbits).
  This can test both LongPermutation and SPNetwork objects"""
  for k in indexes:
    if k>=permutator.numvalues:
      raise Exception('index out of range')
    a = k
    b = permutator.permValue(a)
    c = permutator.permIndex(b)
    assert a==c
    if show:
      print "permValue(%02d)= %02d, permIndex(%02d)= %02d" % (a, b, b, c)
    

def testPermutationAll(permutator, show=False):
  """test all indexes for a permutator object. This can test both LongPermutation and SPNetwork objects"""
  
  rang    = range(permutator.numvalues)
  encrypt = [permutator.permValue(a) for a in rang]
  decrypt = [permutator.permIndex(a) for a in rang]
  plain   = [permutator.permIndex(a) for a in encrypt]
  if show:
    for a, b, c in zip(rang, encrypt, plain):
      print "permValue(%02d)= %02d, permIndex(%02d)= %02d" % (a, b, b, c)
  verifyPermutation(encrypt)
  verifyPermutation(decrypt)
  assert all([a==b for a,b in zip(rang, plain)])


def verifyPermutation(perm):
  sortd = sorted(perm)
  rangd = range(len(perm))
  assert all([a==b for a, b, in zip(rangd, sortd)])
