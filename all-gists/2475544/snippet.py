#!/usr/bin/python
#
# by Nathan Grigg http://nathangrigg.net
#

import sys
import argparse
import os.path
from subprocess import Popen,PIPE

def escape(s):
    s = s.replace("\\","\\\\")
    s = s.replace('"','\\"')
    return s

def parse_arguments():
    parser = argparse.ArgumentParser(
      description="Create a new mail message using Mail.app",
      usage = \
    """mailcat.py [-c cc-addr ...] [-b bcc-addr ...] [-a attachment ...]
                  [-r from-addr] [-s subject] [--send] [--] [to-addr ...]""")
    parser.add_argument('recipient',metavar="to-addr",nargs="*",
      help="message recipient(s)")
    parser.add_argument('-s',metavar="subject",help="message subject")
    parser.add_argument('-c',metavar="addr",nargs="+",
      help="carbon copy recipient(s)")
    parser.add_argument('-b',metavar="addr",nargs="+",
      help="blind carbon copy recipient(s)")
    parser.add_argument('-r',metavar="addr",help="from address")
    parser.add_argument('-a',metavar="file",nargs="+",
      help="attachment(s)")
    parser.add_argument('--input',metavar="file",help="Input file",
      type=argparse.FileType('r'),default=sys.stdin)
    parser.add_argument('--send',action="store_true",help="Send the message")
    #parser.add_argument('-t',action="store_true",help="Extract metadata from inline headers")
    return parser.parse_args()

def make_message(content,subject=None,to_addr=None,from_addr=None,send=False,
  cc_addr=None,bcc_addr=None,attach=None):
    """Uses applescript to create a mail message with the given attributes"""

    if send:
        properties = ["visible:false"]
    else:
        properties = ["visible:true"]
    if subject:
        properties.append('subject:"%s"' % escape(args.s))
    if from_addr:
        properties.append('sender:"%s"' % escape(args.r))
    if len(content) > 0:
        properties.append('content:"%s"' % escape(content))
    properties_string = ",".join(properties)

    template = 'make new %s with properties {%s:"%s"}'
    make_new = []
    if to_addr:
        make_new.extend([template % ("to recipient","address",escape(addr))
          for addr in to_addr])
    if cc_addr:
        make_new.extend([template % ("cc recipient","address",escape(addr))
          for addr in cc_addr])
    if bcc_addr:
        make_new.extend([template % ("bcc recipient","address",escape(addr))
          for addr in bcc_addr])
    if attach:
        make_new.extend([template % ("attachment","file name",
          escape(os.path.abspath(f))) for f in attach])
    if send:
        make_new.append('send')
    if len(make_new) > 0:
        make_new_string = "tell result\n" + "\n".join(make_new) + "\nend tell\n"
    else:
        make_new_string = ""

    script = """tell application "Mail"
    make new outgoing message with properties {%s}
    %s end tell
    """ % (properties_string, make_new_string)

    # run applescript
    p = Popen(['/usr/bin/osascript'],stdin=PIPE,stdout=PIPE)
    p.communicate(script)
    return p.returncode

if __name__ == "__main__":
    args = parse_arguments()
    content = args.input.read()
    code = make_message(content,
        subject     = args.s,
        to_addr     = args.recipient,
        from_addr   = args.r,
        send        = args.send,
        cc_addr     = args.c,
        bcc_addr    = args.b,
        attach      = args.a)
    sys.exit(code)
