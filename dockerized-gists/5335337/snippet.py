#!/usr/bin/env python
from __future__ import with_statement
import smtpd
import asyncore
import sys
import time
import threading

class FakeSMTPD(smtpd.SMTPServer):
    def __init__(self, localaddr, remoteaddr):
        smtpd.SMTPServer.__init__(self, localaddr, remoteaddr)
        self.t0 = time.time()
        self.email_count = 0
        self.bandwith = 0
        self.lock = threading.Lock()
        
    def process_message(self, peer, mailfrom, rcpttos, data):
        with self.lock:
            self.email_count += 1
            self.bandwith += len(data)
            t1 = time.time()
            delta = t1 - self.t0
            print '\r%d messages received into %d seconds. Rate = %.1f mails/s | %d mails/day  Bandwith = %.1f Kb/s' % (
                self.email_count, delta, self.email_count / delta, (self.email_count * 86400) / delta, (self.bandwith / 1024.0) / delta),
        
if __name__ == "__main__":
    port = 25
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    smtpd.DEBUGSTREAM = sys.stdout
    server = FakeSMTPD(("0.0.0.0", port), None)
    
    print "Fake SMTP server listening on port %d" % port
    asyncore.loop()
    
