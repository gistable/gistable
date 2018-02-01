#!/usr/bin/env python
"""
Check that a particular email address exists.
Adam Blinkinsop <blinks@acm.org>

WARNING:
  Checking email addresses in this way is not recommended, and will lead to
  your site being listed in RBLs as a source of abusive traffic. Mail server
  admins do like it when they get connections that don't result in email being
  sent, because spammers often use this technique to verify email addresses.
  (Incidentally, a lot of sites will accept bad addresses and only reject after
  the DATA portion of the SMTP transactions, for this very reason.)

  Additionally, the check is not good in most situations because it doesn't do
  any verification that the owner of the email address wants to receive email
  from you. It does not in any way, shape or form conform to standard confirmed
  opt-in practices. Anyone who uses this technique and then begins sending
  email without going through a confirmation loop is a spammer.

  - Zach White
"""
usage = 'usage: %prog [options] email1 [email2 [...]]'
import logging
import os
import re
import smtplib

# Match the mail exchanger line in nslookup output.
MX = re.compile(r'^.*\s+mail exchanger = (?P<priority>\d+) (?P<host>\S+)\s*$')

def verify(addr, local_addr='john.smith@example.com'):
  """Verify the existance of a single email address."""
  logging.debug('Verifying existance of %r', addr)
  # Find mail exchanger of this address.
  host = addr.rsplit('@', 2)[1]
  p = os.popen('nslookup -q=mx %s' % host, 'r')
  mxes = list()
  for line in p:
    m = MX.match(line)
    if m is not None:
      mxes.append(m.group('host'))
  logging.debug('Found %d mail exchangers for %s.', len(mxes), host)
  if len(mxes) == 0:
    return False
  else:
    host = mxes[0]

  # Connect to the mail server and check.
  logging.debug('Checking address with %s.', host)
  server = smtplib.SMTP(host)
  server.ehlo_or_helo_if_needed()
  code, response = server.docmd('mail from:', 'john.smith@example.com')
  logging.debug('MAIL FROM command returned %d: %r', code, response)
  code, response = server.docmd('rcpt to:', addr)
  logging.debug('RCPT TO command returned %d: %r', code, response)
  server.quit()
  return (code // 100 == 2)

def main(*args, **opts):
  """Handle execution from the command line."""
  for addr in args:
    if verify(addr, local_addr=opts['local_addr']):
      print '%r exists.' % addr
    else:
      print '%s DOES NOT exist.' % addr

def flags():
  """Parse options from the command line."""
  from optparse import OptionParser
  parser = OptionParser(usage=usage)
  parser.add_option('-f', '--from',
      dest='local_addr', default='john.smith@example.com',
      help='email address to appear to be from')
  parser.add_option('-d', '--debug',
      action='store_const', const=logging.DEBUG, dest='log_level',
      help='log everything')
  parser.add_option('-v', '--verbose',
      action='store_const', const=logging.INFO, dest='log_level',
      help='log everything but debugging messages')
  parser.add_option('-q', '--quiet',
      action='store_const', const=logging.ERROR, dest='log_level',
      help='only log errors')
  opts, args = parser.parse_args()
  logging.basicConfig(level=opts.log_level)
  return opts, args

if __name__ == '__main__':
  opts, args = flags()
  main(*args, **opts.__dict__)
