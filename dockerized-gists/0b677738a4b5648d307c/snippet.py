#!/usr/bin/env python
from codecs import open
from contextlib import nested
import re
import sys
from os import path

# The regex ranges below may not work on narrow builds of python < 3.3
# see http://stackoverflow.com/a/25417872/1711188

EMOJI_RE = re.compile(ur"""
    [\U0001F600-\U0001F64F] # emoticons
    |
    [\U0001F300-\U0001F5FF] # symbols & pictographs
    |
    [\U0001F680-\U0001F6FF] # transport & map symbols
    |
    [\U0001F1E0-\U0001F1FF] # flags (iOS)
""", re.VERBOSE)

def uopen(*args):
    return open(*args, encoding="UTF-8")

def remove_emoji(in_fname, out_fname):
    with nested(uopen(in_fname), uopen(out_fname, "w")) as (inf, outf):
        for line in inf:
            outf.write(EMOJI_RE.sub(u'\U000025A1', line))

def main():
    in_fname = sys.argv[1]
    out_fname = sys.argv[2]
    if path.exists(out_fname):
        print >> sys.stderr, "Output file %s already exists" % out_fname
        return 1
    remove_emoji(in_fname, out_fname)
    
if __name__ == "__main__":
    main()