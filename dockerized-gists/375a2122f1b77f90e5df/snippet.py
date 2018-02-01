#!/usr/bin/env python

"""PSSSODLS generator.

Usage:
  psssodls.py [options] [--] <size>

Options:
  -h --help     Show this screen.
  --version     Show version.
  -b            Include box constraints.
"""

import sys

from math import sqrt
from docopt import docopt

def ell(p):
  """This function takes a pair p = [p[0], p[1]] and returns the string
  'l[p[0],p[1]]'."""
  return 'l[{},{}]'.format(p[0], p[1])

def ellell(p):
  return '[{},{}]'.format(ell(p[0]),ell(p[1]))

def alldiff(p):
  """Returns a string representing an all_different constraint over the
  variables in the vector v."""
  return 'alldiff({})'.format(ell(p))

def vecneq(p, q):
  """Returns a string representing an vectorised inequality constraint between
  the two vectors p and q."""
  return 'watchvecneq({}, {})'.format(ellell(p), ellell(q))

def begin(n):
  return """\
MINION 3

**VARIABLES**
DISCRETE l[{},{}] {{0..{}}}

**SEARCH**
PRINT ALL

**CONSTRAINTS**

""".format(n, n, n - 1)

def end():
  return "**EOF**"

def latin_constraints_str(n):
  """Returns a string containing the latin constraints for a square of size
  n."""
  s = '# Latin constraints. \n\n'
  s += "".join([alldiff([i,'_']) + '\n' + alldiff(['_',i]) + '\n' for i in range(n)])
  return s + '\n'

def sdk_positions_box(i,j,p):
  row_offset = p * (i-1)
  column_offset = p * (j-1)
  return [(row_offset + r, column_offset + c) for r in range(p) for c in range(p)]

def box_constraints_str(n):
  p = int(sqrt(n))
  F = [sdk_positions_box(i,j,p) for i in range(1, p + 1) for j in range(1, p + 1)]
  s = '# Box constraints. \n\n'
  for p in F:
    s += 'alldiff([' + ",".join(ell(q) for q in p) + '])' + '\n'
  return s + '\n'

def pandiagonal_sum_a(n, w):
  return ",".join([ell([i % n, (i + w) % n]) for i in range(n)])

def pandiagonal_sum_b(n, w):
  return ",".join([ell([i % n, (w - i) % n]) for i in range(n)])

def pandiagonality_constraints_str(n):
  """Returns a string containing the pandiagonality constraints for a square
  of size n."""
  s = '# Pandiagonality constraints. \n\n'
  pandiagonal_sum_s = str(n*(n - 1)/2)
  for w in range(n):
    s += 'sumgeq([{}],{})\n'.format(pandiagonal_sum_a(n, w), pandiagonal_sum_s)
    s += 'sumleq([{}],{})\n'.format(pandiagonal_sum_a(n, w), pandiagonal_sum_s)
    s += 'sumgeq([{}],{})\n'.format(pandiagonal_sum_b(n, w), pandiagonal_sum_s)
    s += 'sumleq([{}],{})\n\n'.format(pandiagonal_sum_b(n, w), pandiagonal_sum_s)
  return s

def strongly_symmetric_constraints_str(n):
  s = '# Strongly symmetric constraints. \n\n'
  for i in range(n):
    for j in range(n):
      s += 'sumgeq({}, {})\n'.format(ellell([[i,j],[n - 1 - i, n - 1 - j]]), n - 1)
      s += 'sumleq({}, {})\n'.format(ellell([[i,j],[n - 1 - i, n - 1 - j]]), n - 1)
    s += '\n'
  return s

def orthogonality_constraints_str(n):
  """Returns a string containing the orthogonality constraints for a square
  of size n."""
  F = [[(i,j), (j,i)] for i in range(n) for j in range(n)]
  s = '# Orthogonality constraints. \n\n'
  s += "".join([vecneq(p, q) + '\n' for p in F for q in F if p > q])
  return s + '\n'

def psssodls_string(n, boxes):
  """Returns a string which is the entire Minion 3 format constraint program
  for PSSSODLS(n)."""
  s = begin(n)
  s += latin_constraints_str(n)
  if boxes:
    s += box_constraints_str(n)
  s += pandiagonality_constraints_str(n)
  s += strongly_symmetric_constraints_str(n)
  s += orthogonality_constraints_str(n)
  s += end()
  return s

if __name__ == '__main__':
  arguments = docopt(__doc__, version='PSSSODLS 1.0')
  print(psssodls_string(int(arguments['<size>']), arguments['-b']))

