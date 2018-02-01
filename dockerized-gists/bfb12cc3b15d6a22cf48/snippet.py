#!/usr/bin/env python2
# coding=utf-8

from math import *
from time import sleep
import os
import random
import sys

write = sys.stdout.write

### Classy plasma ############################################

class Plasma:

  width, height = 60, 40
  i             = 1
  speed         = 1

  formulas = [
    ["moire",    lambda x, y, i: (sin(tan(cos(x*y*(i/4)))))],
    ["2dsin", lambda x, y, i: (sin((i/2)/((sin(x*i)*(y*i)/200)+1)))],
    ["bars",     lambda x, y, i: (((sin(y*(i/(cos(x))))*tan(x*i))*(i/(x+1)))*(i*(y+1)))],
    ["stripes",  lambda x, y, i: ((sin(x*(i/(cos(y))))*tan(y*i))*(i/(x+1)))],
    ["elbow",    lambda x, y, i: (i/((x*y/20)+1))],
    ["pulsing",  lambda x, y, i: (sin((i/2)/((sin(x*i)*cos(y*i)/200)+1)))],
    ["blobs",    lambda x, y, i: ( sin( sin(x*i) * cos(y*i) ) )],
  ]

  def __init__(_, n=None):
    if n is None:
      n = random.randint(0,len(_.formulas)-1)

    _.name, _.formula = _.formulas[n]

  def render(_):
    i       = _.i
    formula = _.formula

    i = i/1000.0

    lines = []

    for y in range(0, _.height):
      line = []
      for x in range(0, _.width):
        val = formula(x, y, i)
        line.append( greyblock(val) )

      lines.append( ''.join(line) )

    print( '\n'.join(lines) )


  def render_banner(_):
    pos = (sin(float(_.i) / 25.0) + 1.0) / 2 
    # c = (pos * 23) + 232
    c = (pos * (231-196)) + 196
    print( color("%s (%d)" % (_.name, _.i), c, 232) )


  def run(_):
    clear()
    while True:
      home()

      _.render_banner()
      _.render()
      
      _.i += _.speed

      # sleep(0.01)


### Utilities ###############################################

def clear():
  write('\x1b[2J')

def home():
  write('\x1b[1;1H')

def clamp(val, lower, upper):
  return min(upper,max(lower,val))

def color(s, fore, back=None):
  if back is None:
    return '\x1b[38;5;%dm%s' % (fore, s)
  else:
    return '\x1b[38;5;%d;48;5;%dm%s' % (fore, back, s)

GREYCHARS = "@MBHENR#KWXDFPQASUZbdehx*8Gm&04LOVYkpq5Tagns69owz$CIu23Jcfry%1v7l+it[]{}?j|()=~!-/<>\\\"^_';,:`. "
def greychar(val):
  return GREYCHARS[int( clamp(val, 0.0, 1.0) * (len(GREYCHARS)-1) )]

BLOCKS = u"█▓▒░"
def greyblock(val):
  # the 256-colour terminal palette has 23 shades of grey (colors 232 to 255)
  # total colours: 23 greys * 4 shaded blocks = 92 virtual colours

  vcolor = clamp( int(val*92), 0, 92 )

  fore   = 232 + int(vcolor / 4)
  back   = fore + 1
  char   = BLOCKS[vcolor % 4]

  return color(char, fore, back)

def greydient():
  line = [greyblock(n/92.0) for n in range(0, 92)]
  print(''.join(line))

def spectrum():
  print( ' '.join(color(n, n) for n in range(0, 255)) )

def main():
  return '__main__' == __name__

### Main ####################################################

if main():
  if len(sys.argv) > 1:
    num = int(sys.argv[1])
  else:
    num = None

  try:
    Plasma(num).run()
    # greydient()
    # spectrum()
  except KeyboardInterrupt:
    pass

