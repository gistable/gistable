#!/usr/bin/env python

import os
import smtplib
import sys
import time
from optparse import OptionParser

from supervisor import childutils

class ErrorMailer(object):
    def __init__(self, address, processes=None):
        self.address = address
        self.processes = processes
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.mailcmd = "mail"

    def run(self):
        last_email = {}
        while True:
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)

            if headers['eventname'] not in ('PROCESS_STATE_EXITED', 'PROCESS_LOG_STDERR'):
                childutils.listener.ok(self.stdout)
                continue

            if headers['eventname'] == 'PROCESS_STATE_EXITED':
                pheaders, pdata = childutils.eventdata(payload+'\n')

                if int(pheaders['expected']):
                    childutils.listener.ok(self.stdout)
                    continue

                msg = ('Process %(processname)s in group %(groupname)s exited '
                       'unexpectedly (pid %(pid)s) from state %(from_state)s' %
                       pheaders)
            
                subject = ' %s crashed at %s' % (pheaders['processname'],
                                                 childutils.get_asctime())

                # self.stderr.write('unexpected exit, mailing\n')
                # self.stderr.flush()

                self.mail(subject, msg)

                childutils.listener.ok(self.stdout)
            else: # PROCESS_LOG_STDERR
                pheaders, pdata = childutils.eventdata(payload)

                name = pheaders['processname']
                now = time.time()
                if now - last_email.get(name, 0) < 30:
                    childutils.listener.ok(self.stdout)
                    continue
                last_email[name] = now

                subject = ('Process %(processname)s in group %(groupname)s wrote to stderr'
                       % pheaders)

                # self.stderr.write('wrote to stderr, mailing\n')
                # self.stderr.flush()

                self.mail(subject, pdata.strip())

                childutils.listener.ok(self.stdout)

    def mail(self, subject, msg):
        fromaddress = "root@localhost"
        body = "\r\n".join((
            "From: %s" % fromaddress,
            "To: %s" % self.address,
            "Subject: %s" % subject,
            "",
            msg,
        ))
        server = smtplib.SMTP('localhost')
        server.sendmail(fromaddress, [self.address], body)
        server.quit()

def build_parser():
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option("-p", "--process", dest="processes", help="Process name", action="append")
    parser.add_option("-m", "--address", dest="address", help="Email address")
    return parser

def main():
    parser = build_parser()
    options, system = parser.parse_args()
    if not options.address:
        parser.error("must specify an email address")

    prog = ErrorMailer(processes=options.processes, address=options.address)
    prog.run()

if __name__ == '__main__':
    main()
