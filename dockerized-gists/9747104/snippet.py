#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Written by Titus von der Malsburg <malsburg@posteo.de>, March 2014.

# This is a simple script for converting vCard files to
# org-contacts.  There is one mandatory argument: the name of the
# vCard file.  The result is printed to standard out.

# Usage:
#
#     python vcard2org-contacts.py contacts.vcf > contacts.org
#

# Issues:
#
# The LABEL property in the Forrest Gump example (from Wikipedia) is
# not handled correctly:
#
#    LABEL;TYPE=WORK:100 Waters Edge\nBaytown, LA 30314\nUnited States of America
#
# The part after the comma is missing.  That seems to be due to a bug
# in vobject.

import sys
import io
import dateutil.parser
import vobject
import codecs

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

template = "  :%s: %s%s"
prefix = "*"
indentation = "  "

def flatten(l):
  '''Flatten a arbitrarily nested lists and return the result as a single list.
  '''
  ret = []
  for i in l:
    if isinstance(i, list) or isinstance(i, tuple):
      ret.extend(flatten(i))
    else:
      ret.append(i)
  return ret

if __name__=="__main__":

  if len(sys.argv) != 2:
    raise ValueError("Please specify exactly one vCard file.")

  fname = sys.argv[1]
  stream = io.open(fname, "r", encoding="utf-8")
  vcards = vobject.readComponents(stream)

  for vcard in vcards:

    note = ""

    print "%s %s" % (prefix, vcard.fn.value)
    print indentation + ":PROPERTIES:"

    for p in vcard.getChildren():

      if p.name in ("VERSION", "PRODID", "FN") or p.name.startswith("X-"):
        continue

      if p.name == "NOTE":
        note = p.value
        continue

      name = p.name
      value = p.value

      # Special treatment for some fields:

      if p.name == "ORG":
        try:
          value = ", ".join(flatten(p.value))
        except:
          print p.value

      if p.name == "N":
        value = "%s;%s;%s;%s;%s" % (p.value.family, p.value.given,
                                    p.value.additional, p.value.prefix,
                                    p.value.suffix)

      if p.name == "ADR":
        # TODO Make the formatting sensitive to X-ABADR:
        value = (p.value.street, p.value.code + " " + p.value.city,
                 p.value.region, p.value.country, p.value.extended, p.value.box)
        value = ", ".join([x for x in value if x!=''])
        name = "ADDRESS"

      if p.name == "REV":
        value = dateutil.parser.parse(p.value)
        value = value.strftime("[%Y-%m-%d %a %H:%M]")

      if p.name == "TEL":
        name = "PHONE"

      # Collect type attributes:
      attribs = ", ".join(p.params.get("TYPE", []))
      if attribs:
        attribs = " (%s)" % attribs

      # Make sure that there are no newline chars left as that would
      # break org's property format:
      value = value.replace("\n", ", ")

      print template % (name, value, attribs)

    print indentation + ":END:"

    if note:
      print note
