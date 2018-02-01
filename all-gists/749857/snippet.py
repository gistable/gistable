#!/usr/bin/python
# -*- coding: utf-8 -*-

# launchctl unload /System/Library/LaunchDaemons/com.apple.syslogd.plist
# launchctl load /System/Library/LaunchDaemons/com.apple.syslogd.plist

from twisted.internet import reactor, stdio, defer
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
import time, re, math, json

#<22>Nov  1 00:12:04 gleicon-vm1 postfix/smtpd[4880]: connect from localhost[127.0.0.1]
severity = ['emerg', 'alert', 'crit', 'err', 'warn', 'notice', 'info', 'debug', ]

facility = ['kern', 'user', 'mail', 'daemon', 'auth', 'syslog', 'lpr', 'news',
    'uucp', 'cron', 'authpriv', 'ftp', 'ntp', 'audit', 'alert', 'at', 'local0',
    'local1', 'local2', 'local3', 'local4', 'local5', 'local6', 'local7',]

fs_match = re.compile("<(.+)>(.*)", re.I)

class SyslogdProtocol(LineReceiver):
    delimiter = '\n'
    def connectionMade(self):
        print 'Connection from %r' % self.transport


    def lineReceived(self, line):
        k = {}
        k['line'] = line.strip()
        (fac, sev) = self._calc_lvl(k['line'])
        k['host'] = self.transport.getHost().host
        k['tstamp'] = time.time()
        k['facility'] = fac
        k['severity'] = sev
        print json.dumps(k)

    def _calc_lvl(self, line):
        lvl = fs_match.split(line)
        if lvl and len(lvl) > 1:
            i = int(lvl[1])
            fac = int(math.floor(i / 8))
            sev = i - (fac * 8)
            return (facility[fac], severity[sev])
        return (None, None)

class SyslogdFactory(Factory):
    protocol = SyslogdProtocol

def main():
    factory = SyslogdFactory()
    reactor.listenTCP(25000, factory, 10)
    reactor.run()

if __name__ == '__main__':
    main()
