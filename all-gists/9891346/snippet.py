#!/usr/bin/env python3

# inspired by https://github.com/busyloop/lolcat

import sys
import re
import os
from math import ceil
from colorsys import hsv_to_rgb
from unicodedata import east_asian_width

try:
  # in https://github.com/lilydjwg/winterpy
  from colorfinder import hex2term_accurate as hex2term
except ImportError:
  def hex2term(c):
    red, green, blue = (int(x, 16) for x in (c[1:3], c[3:5], c[5:7]))

    # from ruby-paint
    gray_possible = True
    sep = 42.5
    gray = False

    while gray_possible:
      if red < sep or green < sep or blue < sep:
        gray = red < sep and green < sep and blue < sep
        gray_possible = False
      sep += 42.5

    if gray:
      return 232 + (red + green + blue) // 33
    else:
      return 16 + sum(6 * x // 256 * 6 ** i
                      for i, x in enumerate((blue, green, red)))

def get_terminal_size(fd=1):
  """
  Returns height and width of current terminal. First tries to get
  size via termios.TIOCGWINSZ, then from environment. Defaults to 25
  lines x 80 columns if both methods fail.

  :param fd: file descriptor (default: 1=stdout)

  from: http://blog.taz.net.au/2012/04/09/getting-the-terminal-size-in-python/
  """
  try:
    import fcntl, termios, struct
    hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
  except Exception:
    try:
      hw = (os.environ['LINES'], os.environ['COLUMNS'])
    except Exception:
      hw = (25, 80)

  return hw

COLOR_CODE_RE = re.compile(r'\x1b\[(?:\d*)(?:;\d+)*[mK]')
init_width = 0

def rainbow(freq, i):
  h = i * freq
  r, g, b = (int(round(x * 255)) for x in hsv_to_rgb(h, 1, 1))
  return "#%02X%02X%02X" % (r, g, b)

def colorline(line, lineno=0, *, width=0):
  global init_width
  term_w = get_terminal_size(2)[1]
  if not width:
    if not init_width:
      init_width = term_w - 1
    width = init_width / 2
  freq = 1 / width

  col = 0
  line = COLOR_CODE_RE.sub('', line)
  for c in line:
    sys.stdout.write(colored(c, rainbow(freq, col+lineno)))
    if east_asian_width(c) in 'WF':
      col += 2
    else:
      col += 1
  sys.stdout.write('\x1b[0m') # reset
  return ceil(col / term_w)

def colored(ch, color):
  c = hex2term(color)
  return '\x1b[01;0;38;5;{c}m{ch}'.format(c=c, ch=ch)

if __name__ == '__main__':
  import argparse
  import signal

  parser = argparse.ArgumentParser(description='Okay, no unicorns. But rainbows! In Python.')
  parser.add_argument('-w', '--width', type=int, metavar='N',
                      help='rainbow width. default: half of terminal width-1')
  parser.add_argument('-i', '--ignore-interrupts', action='store_true',
                      help='ignore interrupt signals')
  parser.add_argument('files', nargs='*', metavar='FILE',
                      type=argparse.FileType('r'),
                      help='files to cat. default: stdin')
  args = parser.parse_args()

  if args.ignore_interrupts:
    signal.signal(signal.SIGINT, signal.SIG_IGN)

  files = args.files or [sys.stdin]
  try:
    i = 0
    for f in files:
      for line in f:
        inc = colorline(line, i, width=args.width)
        i += inc
  except KeyboardInterrupt:
    print()
