#!/usr/bin/env python
'''
Quick and dirty hack to get the SIKS dissertation list in LaTeX.
'''
import argparse, re, operator, itertools, sys

parser = argparse.ArgumentParser(
  description='Convert SIKS dissertation list to LaTeX.')
parser.add_argument('txt')
parser.add_argument('tex')
parser.add_argument('-n', '--output-lines', type=int, default=100)

args = parser.parse_args()

dissertations = []
with open(args.txt, 'r') as f:
  for line in f:
    match =  re.search(r'\d{4}-\d+', line)
    if match:
      diss_id = match.group(0)
      author = f.next().strip()
      title = f.next().strip()
      dissertations.append((diss_id, author, title))

sorted_diss = sorted(dissertations, key=operator.itemgetter(0), reverse=True)

with open(args.tex, 'w') as f:
  latex_cmd = r'\newcommand{\SIKSdiss}[3]{{\bf #1}\hspace*{1ex}#2, {\it #3.}\\}'
  f.write('%s\n\n' % latex_cmd)
  for diss in sorted_diss[:args.output_lines]:
    f.write('\\SIKSdiss{%s}{%s}{%s}\n' % diss)