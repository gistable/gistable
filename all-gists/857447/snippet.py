#!/bin/env python

from smtpd import SMTPChannel, SMTPServer
import asyncore


class LMTPChannel(SMTPChannel):
  # LMTP "LHLO" command is routed to the SMTP/ESMTP command
  def smtp_LHLO(self, arg):
    self.smtp_HELO(arg)

class LMTPServer(SMTPServer):
  def __init__(self, localaddr, remoteaddr):
    SMTPServer.__init__(self, localaddr, remoteaddr)

  def process_message(self, peer, mailfrom, rcpttos, data):
    print 'Receiving message from:', peer
    print 'Message addressed from:', mailfrom
    print 'Message addressed to  :', rcpttos
    print 'Message length        :', len(data)
    print 'Message               :', data
    return

  def handle_accept(self):
    conn, addr = self.accept()
    channel = LMTPChannel(self, conn, addr)

server = LMTPServer(('localhost', 10025), None)

asyncore.loop()