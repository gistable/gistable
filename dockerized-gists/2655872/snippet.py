#!/bin/env python

'''This is a script which runs an MTR (matt's traceroute)
against a target hosts - meant to be triggered by a
smokeping alert. Output is emailed and saved to log.'''

import argparse, datetime, subprocess, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_FROM = 'SmokeMTR <from_email@your_domain.com>'
MAIL_TO   = 'to_email@your_domain.com'
SMTP_HOST = 'your_smtp_host'
LOG_FILE  = '/tmp/smokealert.out'

def parse_args():
  """Define the argparse parameters to accept for smokeping args:
  name-of-alert, target, loss-pattern, rtt-pattern, hostname"""
  parser = argparse.ArgumentParser(description='Example with non-optional arguments')
  parser.add_argument('alert', action="store")
  parser.add_argument('target', action="store")
  parser.add_argument('loss', action="store")
  parser.add_argument('rtt', action="store")
  parser.add_argument('host', action="store")
  return(parser.parse_args())


def mtr_host(parsed):
  """Run a matt's traceroute against the problematic host and append the results to
  a list which will be used to log to file and send email"""
  m = []
  m.append( '===== %s =====\n' % str(datetime.datetime.now())[:19] )
  m.append( 'Alert: %s\n' % parsed.alert )
  m.append( 'Loss: %s\n' % parsed.loss )
  m.append( 'Round Trip Time: %s\n' % parsed.rtt )
  m.append( '%s: %s\n\n' % (parsed.target, parsed.host) )
  m.append( 'Matts traceroute to: %s\n' % parsed.host )
  m.append( cmd_out( ('/usr/sbin/mtr --report --report-cycles 10 %s' % parsed.host).split() ))

  mail_alert(subject=parsed.host + " alert", body=''.join(m))
  
  f = open(LOG_FILE, 'a')
  f.write( "".join(m) + '\n' )
  f.close()

def cmd_out(args, **kwds):
  """cmd_out uses the subprocess lib to grab the output of a system command.
  There are easier ways to this but apparently this is the 'best practice'
  method according to: http://goo.gl/LfYhP"""
  kwds.setdefault("stdout", subprocess.PIPE)
  kwds.setdefault("stderr", subprocess.STDOUT)
  p = subprocess.Popen(args, **kwds)
  return p.communicate()[0]

def mail_alert(subject="Smokeping alert", body=""):
  '''Generate an HTML and TXT encoded mail with given subject and body'''

  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg['Subject'] = subject
  msg['From'] = MAIL_FROM
  msg['To'] = MAIL_TO

  # Create the body of the message (a plain-text and an HTML version).
  text = body
  html = """\
  <pre>
    %s
  </pre>
  """ % body

  # Record the MIME types of both parts - text/plain and text/html.
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(html, 'html')

  # Attach parts into message container.
  # According to RFC 2046, the last part of a multipart message, in this case
  # the HTML message, is best and preferred.
  msg.attach(part1)
  msg.attach(part2)

  # Send the message via local SMTP server.
  s = smtplib.SMTP(SMTP_HOST)
  # sendmail function takes 3 arguments: sender's address, recipient's address
  # and message to send - here it is sent as one string.
  s.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
  s.quit()


if __name__ == '__main__':
  mtr_host(parse_args())