# http://notmysock.org/blog/hacks/a-twisted-dns-story.html
# http://blog.inneoin.org/2009/11/i-used-twisted-to-create-dns-server.html
# twistd -y dns.py
import socket

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.names import dns
from twisted.names import client, server


CHANGE = 'example.com'
TO = '127.0.0.1'
TTL = 60

class DNSServerFactory(server.DNSServerFactory):
    def gotResolverResponse(self, (ans, auth, add), protocol, message, address):
        qname = message.queries[0].name.name
        if CHANGE in qname:
            for answer in ans:
                if answer.type != dns.A:
                    continue
                if CHANGE not in answer.name.name:
                    continue
                
                answer.payload.address = socket.inet_aton(TO)
                answer.payload.ttl = TTL

        args = (self, (ans, auth, add), protocol, message, address)
        return server.DNSServerFactory.gotResolverResponse(*args)


verbosity = 0

resolver = client.Resolver(servers=[('4.2.2.2', 53)])
factory = DNSServerFactory(clients=[resolver], verbose=verbosity)
protocol = dns.DNSDatagramProtocol(factory)
factory.noisy = protocol.noisy = verbosity

reactor.listenUDP(53, protocol)
reactor.listenTCP(53, factory)
reactor.run()