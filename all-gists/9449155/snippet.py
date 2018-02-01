#!/usr/bin/env python
#
# author: github.com/jbenet
# license: MIT
#
# tikz2svg: convert tikz input into svg
# depends on:
# - pdflatex: comes with your tex dist
# - pdf2svg: brew install pdf2svg

import os
import sys
import hashlib
import functools
from subprocess import Popen, PIPE


class cmds(object):
  pdflatex = 'pdflatex --shell-escape -file-line-error -interaction=nonstopmode --'
  pdf2svg = 'pdf2svg texput.pdf out.svg'


latex_doc ='''
\documentclass[border=2bp]{standalone}
\usepackage{tikz}
\\begin{document}
\\begingroup
\\tikzset{every picture/.style={scale=1}}
%(content)s
\endgroup
\end{document}
'''

# util to run command in a subprocess, and communicate with it.
def run(cmd, stdin=None, exit_on_error=True):
  # print '>', cmd
  p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
  if stdin:
    p.stdin.write(stdin)
    p.stdin.close()
  p.wait()

  # error out if necessary
  if p.returncode != 0 and exit_on_error:
    print '>', cmd
    print 'Error.'
    print '-' * 20, 'STDIN'
    print stdin
    print '-' * 20, 'STDOUT'
    print p.stdout.read()
    print '-' * 20, 'STDERR'
    print p.stderr.read()
    sys.exit(p.returncode)

  return p.stdout.read()

# memoize with a file cache.
def memoize_in_file(fn):
  @functools.wraps(fn)
  def memoized(*args, **kwds):
    i = fn.__name__ + str(*args) + str(**kwds)
    h = hashlib.sha1(i).hexdigest()
    if os.path.exists(h):
      with open(h) as f:
        return f.read()

    out = fn(*args, **kwds)
    with open(h, 'w') as f:
      f.write(out)
    return out
  return memoized


# conversion functions
def tikz2tex(tikz):
  return latex_doc % {'content': tikz}

def tex2pdf(tex):
  return run(cmds.pdflatex.split(' '), stdin=tex)

def pdf2svg(pdf):
  run(cmds.pdf2svg)
  with open('out.svg') as f:
    return f.read()

@memoize_in_file
def tikz2svg(tikz):
  tex = tikz2tex(tikz)
  pdf = tex2pdf(tex)
  svg = pdf2svg(pdf)
  return svg

# move to tmp because latex litters :(
def chdir(inp):
  h = hashlib.sha1(inp).hexdigest()
  d = '/tmp/%s' % h
  run('mkdir -p %s' % d, exit_on_error=False)
  os.chdir(d)

if __name__ == '__main__':
  if '-h' in sys.argv or '--help' in sys.argv:
    print 'Usage: %s [<file>]' % sys.argv[0]
    print 'Outputs svg conversion of tikz input (files or stdin).'
    sys.exit(0)

  import fileinput
  lines = ''.join([l for l in fileinput.input()])
  chdir(lines)
  print tikz2svg(lines)
