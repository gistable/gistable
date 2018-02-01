#!/usr/bin/python

# Python 2 format converter

from __future__ import division

import sys

sizes = {
  'bit': 0.125,
  'kbit': 125,
  'mbit': 125000,
  'b': 1,
  'kb': 1000,
  'kib': 1024,
  'mb': 1000000,
  'mib': 1048576
}

def parseDecimal(arg):
  return int(arg)

def parseHex(arg):
  # Drop 0x
  literal = arg[2:] if arg.startswith('0x') else arg
  return int(literal, 16)

def parseSize(format):
  def high(arg):
    return int(arg) * sizes[format]
  return high

def exportSize(format):
  def high(arg):
    return str(arg / sizes[format]) + ' ' + format
  return high

if len(sys.argv) <= 2:
  print >> sys.stderr, 'Not enough args.'
  exit(1)

inmode = sys.argv[1]
outmode = sys.argv[2]

if len(sys.argv) == 3:
  value = 1
else:
  value = sys.argv[3]

try:
  infunc = {
    'hex': parseHex,
    'dec': parseDecimal
  }[inmode]
except KeyError:
  infunc = parseSize(inmode)

try:
  outfunc = {
    'hex': hex,
    'dec': str
  }[outmode]
except KeyError:
  outfunc = exportSize(outmode)

print outfunc(infunc(value))