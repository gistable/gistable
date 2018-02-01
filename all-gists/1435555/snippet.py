#!/usr/bin/python

# Python program that can send out M-SEARCH messages using SSDP (in server
# mode), or listen for SSDP messages (in client mode).

import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900

MS = 'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)

class Base(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        first_line = datagram.rsplit('\r\n')[0]
        print "Received %s from %r" % (first_line, address, )

    def stop(self):
        pass

class Server(Base):
    def __init__(self, iface):
        self.iface = iface
        task.LoopingCall(self.send_msearch).start(6) # every 6th seconds

    def send_msearch(self):
        port = reactor.listenUDP(0, self, interface=self.iface)
        print "Sending M-SEARCH..."
        port.write(MS, (SSDP_ADDR, SSDP_PORT))
        reactor.callLater(2.5, port.stopListening) # MX + a wait margin

class Client(Base):
    def __init__(self, iface):
        self.iface = iface
        self.ssdp = reactor.listenMulticast(SSDP_PORT, self, listenMultiple=True)
        self.ssdp.setLoopbackMode(1)
        self.ssdp.joinGroup(SSDP_ADDR, interface=iface)

    def stop(self):
        self.ssdp.leaveGroup(SSDP_ADDR, interface=self.iface)
        self.ssdp.stopListening()

def main(mode, iface):
    klass = Server if mode == 'server' else Client
    obj = klass(iface)
    reactor.addSystemEventTrigger('before', 'shutdown', obj.stop)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s <server|client> <IP of interface>" % (sys.argv[0], )
        sys.exit(1)
    mode, iface = sys.argv[1:]
    reactor.callWhenRunning(main, mode, iface)
    reactor.run()
