#!/usr/bin/env python
# coding=utf-8
# License: Public domain (CC0)
# Isaac Turner 2016/12/05

from __future__ import print_function

import difflib
import re

_no_eol = "\ No newline at end of file"
_hdr_pat = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")

def make_patch(a,b):
  """
  Get unified string diff between two strings. Trims top two lines.
  Returns empty string if strings are identical.
  """
  diffs = difflib.unified_diff(a.splitlines(True),b.splitlines(True),n=0)
  try: _,_ = next(diffs),next(diffs)
  except StopIteration: pass
  # diffs = list(diffs); print(diffs)
  return ''.join([d if d[-1] == '\n' else d+'\n'+_no_eol+'\n' for d in diffs])

def apply_patch(s,patch,revert=False):
  """
  Apply patch to string s to recover newer string.
  If revert is True, treat s as the newer string, recover older string.
  """
  s = s.splitlines(True)
  p = patch.splitlines(True)
  t = ''
  i = sl = 0
  (midx,sign) = (1,'+') if not revert else (3,'-')
  while i < len(p) and p[i].startswith(("---","+++")): i += 1 # skip header lines
  while i < len(p):
    m = _hdr_pat.match(p[i])
    if not m: raise Exception("Bad patch -- regex mismatch [line "+str(i)+"]")
    l = int(m.group(midx))-1 + (m.group(midx+1) == '0')
    if sl > l or l > len(s):
      raise Exception("Bad patch -- bad line num [line "+str(i)+"]")
    t += ''.join(s[sl:l])
    sl = l
    i += 1
    while i < len(p) and p[i][0] != '@':
      if i+1 < len(p) and p[i+1][0] == '\\': line = p[i][:-1]; i += 2
      else: line = p[i]; i += 1
      if len(line) > 0:
        if line[0] == sign or line[0] == ' ': t += line[1:]
        sl += (line[0] != sign)
  t += ''.join(s[sl:])
  return t

#
# Testing
#

import random
import string
import traceback
import sys
import codecs

def test_diff(a,b):
  mp = make_patch(a,b)
  try:
    assert apply_patch(a,mp) == b
    assert apply_patch(b,mp,True) == a
  except Exception as e:
    print("=== a ===")
    print([a])
    print("=== b ===")
    print([b])
    print("=== mp ===")
    print([mp])
    print("=== a->b ===")
    print(apply_patch(a,mp))
    print("=== a<-b ===")
    print(apply_patch(b,mp,True))
    traceback.print_exc()
    sys.exit(-1)

def randomly_interleave(*args):
  """ Randomly interleave multiple lists/iterators """
  iters = [iter(x) for x in args]
  while iters:
    i = random.randrange(len(iters))
    try:
      yield next(iters[i])
    except StopIteration:
      # swap empty iterator to end and remove
      iters[i],iters[-1] = iters[-1],iters[i]
      iters.pop()

def rand_ascii():
  return random.choice(string.printable)

def rand_unicode():
  a = u"\\u%04x" % random.randrange(0x10000)
  # return a.decode('utf-8')
  return str(codecs.encode(a, 'utf-8'))

def generate_test(nlines=10,linelen=10,randchar=rand_ascii):
  """
  Generate two strings with approx `nlines` lines, which share approx half their
  lines. Then run the diff/patch test unit with the two strings.
  Lines are random characters and may include newline / linefeeds.
  """
  aonly,bonly,nshared = (random.randrange(nlines) for _ in range(3))
  a  = [ ''.join([randchar() for _ in range(linelen)]) for _ in range(aonly)]
  b  = [ ''.join([randchar() for _ in range(linelen)]) for _ in range(bonly)]
  ab = [ ''.join([randchar() for _ in range(linelen)]) for _ in range(nshared)]
  a = randomly_interleave(a,ab)
  b = randomly_interleave(b,ab)
  test_diff(''.join(a),''.join(b))

def std_tests():
  test_diff("asdf\nhamster\nmole\nwolf\ndog\ngiraffe",
            "asdf\nhampster\nmole\nwolf\ndooog\ngiraffe\n")
  test_diff("asdf\nhamster\nmole\nwolf\ndog\ngiraffe",
            "hampster\nmole\nwolf\ndooog\ngiraffe\n")
  test_diff("hamster\nmole\nwolf\ndog",
            "asdf\nhampster\nmole\nwolf\ndooog\ngiraffe\n")
  test_diff("", "")
  test_diff("", "asdf\nasf")
  test_diff("asdf\nasf","xxx")
  # Things can get nasty, we need to be able to handle any input
  # see https://docs.python.org/3/library/stdtypes.html
  test_diff("\x0c", "\n\r\n")
  test_diff("\x1c\v", "\f\r\n")

def main():
  print("Testing...")
  std_tests()
  print("Testing random ASCII...")
  for _ in range(50): generate_test(50,50,rand_ascii)
  print("Testing random unicode...")
  for _ in range(50): generate_test(50,50,rand_unicode)
  print("Passed ✓")

if __name__ == '__main__': main()
