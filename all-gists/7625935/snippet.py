#!/usr/bin/env python

# Simple script for finding and counting the color pages in a PDF
# Copyright (C) 2013 Antonio Garcia-Dominguez
# Licensed under the GPLv3
#
# This script is based on the following thread (thanks for the tip!):
#
#   http://tex.stackexchange.com/questions/53493

import logging
import re
import subprocess
from os import path, access, R_OK

VERSION = "1.0.4"

RE_FLOAT = re.compile("[01].[0-9]+")
CMYK_NCOLORS = 4

logging.basicConfig(level=logging.ERROR)


def is_color(c, m, y, k):
  return c > 0 or m > 0 or y > 0


def cmyk_per_page(pdf_file):
  if not path.isfile(pdf_file):
    raise Exception("{} does not exist or is not a file".format(pdf_file))
  if not access(pdf_file, R_OK):
    raise Exception("{} is not readable".format(pdf_file))

  gs_inkcov = subprocess.Popen(
      ["gs", "-o", "-", "-sDEVICE=inkcov", pdf_file],
      stdout=subprocess.PIPE)

  for raw_line in iter(gs_inkcov.stdout.readline, b''):
    line = raw_line.decode('utf8').rstrip()
    logging.debug("Read line %s", line)

    fields = line.split()
    if (len(fields) >= CMYK_NCOLORS
        and all(RE_FLOAT.match(fields[i]) for i in range(CMYK_NCOLORS))):
      cmyk = tuple(float(value) for value in fields[0:CMYK_NCOLORS])
      logging.debug("Extracted fields %s", cmyk)
      yield cmyk


def count_page_types(pdf_file):
  nb, nc = 0, 0
  for page in cmyk_per_page(pdf_file):
    if is_color(*page):
      nc += 1
    else:
      nb += 1
  return (nb, nc)


def find_color_pages(pdf_file):
  for n, page in enumerate(cmyk_per_page(pdf_file), 1):
    if is_color(*page):
      logging.debug("Page %d is a color page", n)
      yield (n, page)


if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="""Lists or counts the
    colour pages of a PDF file on standard output. The utility
    requires having the 'gs' tool from Ghostscript 9.05 or later
    installed and available through the PATH.""", version=VERSION)

  parser.add_argument("file", help="PDF file to be analyzed")
  parser.add_argument("--count", "-c", action='store_true',
                      help="Print the number of pages instead of listing them")
  parser.add_argument("--debug", "-d", action='store_true',
                      help="Enables verbose debugging output")
  parser.add_argument("--noheader", "-H", action='store_true',
                      help="Disables the first header line")
  parser.add_argument("--pcolor", "-C", metavar="PC", type=float,
                      help="Color page price (for total cost report, " +
                           "requires --pblack as well)")
  parser.add_argument("--pblack", "-B", metavar="PB", type=float,
                      help="B/W page price (for total cost report, " +
                           "requires --pcolor as well)")
  args = parser.parse_args()

  if args.debug:
    logging.getLogger('').setLevel(logging.DEBUG)
  if args.pcolor is not None and args.pblack is None:
    raise Exception(
      "Page price was specified for color but not for B/W pages")
  if args.pblack is not None and args.pcolor is None:
    raise Exception(
      "Page price was specified for B/W but not for color pages")

  if args.count:
    print(count_page_types(args.file)[1])
  elif args.pcolor is not None and args.pblack is not None:
    nb, nc = count_page_types(args.file)
    total_cost = args.pblack * nb + args.pcolor * nc
    print(("Total cost ({0:d} B/W @ {1:3.6g}/page "
           + "and {2:d} color @ {3:3.6g}/page): {4:3.6g}")
          .format(nb, args.pblack, nc, args.pcolor, total_cost))
  else:
    if not args.noheader:
      print("\t".join(("n", "c", "m", "y", "k")))
    for n, cmyk in find_color_pages(args.file):
      print("\t".join((str(s) for s in (n,) + cmyk)))
