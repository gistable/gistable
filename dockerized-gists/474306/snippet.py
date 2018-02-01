#!/usr/bin/env python

import cStringIO
import json
import sys

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers.web import JavascriptLexer

def main():
    pretty_input = cStringIO.StringIO()
    if len(sys.argv) == 1:
        infile = sys.stdin
    elif len(sys.argv) == 2:
        infile = open(sys.argv[1], 'rb')
    else:
        raise SystemExit("{0} [infile [outfile]]".format(sys.argv[0]))

    try:
        obj = json.load(infile)
    except ValueError, e:
        raise SystemExit(e)

    json.dump(obj, pretty_input, sort_keys=True, indent=4)
    pretty_input.write('\n')
    highlight(pretty_input.getvalue(), JavascriptLexer(),
        TerminalFormatter(), sys.stdout)

if __name__ == '__main__':
    main()
