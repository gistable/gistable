#!/usr/bin/python

from __future__ import print_function
import sys

if sys.version_info.major == 2:
  def prompt(s = ">>> "): return raw_input(s)
else:
  def prompt(s = ">>> "): return input(s)

def f(line): return "".join(reversed(line))

if sys.stdin.isatty():
  try:
    import readline
  except ImportError:
    pass
  while True:
    try:
      line = prompt()
    except EOFError:
      print(); break
    if line: print(f(line))
else:
  for line in ( l.rstrip("\n") for l in sys.stdin ):
    print(f(line))
