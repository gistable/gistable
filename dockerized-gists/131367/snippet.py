#!/usr/bin/env python
#
# Python code for http://www.cloudera.com/blog/2009/06/17/analyzing-apache-logs-with-piganalyzing-apache-logs-with-pig/

import sys
import math

def rescale(values, low=0, high=4095):
  """Linearly rescales values to be strictly between low and high."""
  maxval = max(values)
  minval = min(values)
  scale = float(high-low)/float(maxval-minval)
  return [ low + scale*(x - minval) for x in values ]

def encode(i):
  """
  Implements the "extended encoding" at 
  http://code.google.com/apis/chart/formats.html#extended
  """
  code = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-."
  i = int(i)
  assert len(code) == 64
  assert i >= 0
  assert i < 64*64
  return "%s%s" % (code[i/64], code[i%64])

def build_map_url(keys, values, area="world"):
  """
  Builds a Google chart API map URL.

  Keys are country or state codes within area, and values
  should be values that can be encoded.
  """
  # See http://code.google.com/apis/chart/types.html#maps
  return "http://chart.apis.google.com/chart?cht=t&chs=440x220&chco=FFFFFF,FFFFFF,148BCF" + \
         "&chtm=%s&chld=%s&chd=e:%s" % (area, "".join(keys), "".join(map(encode, values)))

def print_url(header, url):
  print "%s: <img src='%s'><br>" % (header, url)

def read_tsv(filename):
  return map(lambda line: line.rstrip().split("\t"), file(filename))

def main():
  # Read by_country data, filter out null countries, and transpose it.
  lines = read_tsv("by_country.tsv")
  lines = filter(lambda x: x[0], lines)
  countries, hits, bytes = zip(*lines)
  # Take the log of the data and rescale.
  hits = rescale(map(math.log, map(float, hits)))
  bytes = rescale(map(math.log, map(float, bytes)))
  print_url("Bytes by country:", build_map_url(countries, bytes))
  print_url("Hits by country:", build_map_url(countries, hits))

  # Read by_state (US data), filter out the null, and transpose
  lines = read_tsv("by_state.tsv")
  lines = filter(lambda x: x[0], lines)
  states, hits, bytes = zip(*lines)
  # Take logs and rescale
  hits = rescale(map(math.log, map(float, hits)))
  bytes = rescale(map(math.log, map(float, bytes)))
  print_url("Bytes by state: ", build_map_url(states, bytes, "usa"))
  print_url("Hits by state: ", build_map_url(states, hits, "usa"))

if __name__ == "__main__":
  main()