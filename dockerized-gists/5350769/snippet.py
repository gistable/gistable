#!/usr/bin/env python
"""
nntp-pull

Pulls all the messages from a newsgroup and puts them in a local mbox file.

Copyright (c) Keith Gaughan, 2013.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import contextlib
import email
import mailbox
import nntplib
import sys

import docopt


USAGE = """Usage:
  nntp-pull --host=HOST [--port=PORT] GROUP MBOX
  nntp-pull -h | --help
  nntp-pull --version

Options:
  -h, --help   Show this screen.
  --version    Show version
  --host=HOST  NNTP host to connect to.
  --port=PORT  NNTP host port to connect to.
               [default: %d]
""" % (nntplib.NNTP_PORT,)


def main():
    args = docopt.docopt(USAGE, sys.argv[1:], version='0.1.0')

    with contextlib.closing(mailbox.mbox(args['MBOX'])) as mbox:
        conn = nntplib.NNTP(args['--host'], port=int(args['--port']))
        try:
            _, _, first, last, _ = conn.group(args['GROUP'])
            for i in xrange(int(first), int(last) + 1):
                _, _, _, lines = conn.article(str(i))
                msg = email.message_from_string(nntplib.CRLF.join(lines))
                mbox.add(msg)
        finally:
            conn.quit()
    return 0


if __name__ == '__main__':
    sys.exit(main())