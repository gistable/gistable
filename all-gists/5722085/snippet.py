from collections import Mapping

from twisted.names import dns, server, client, cache
from twisted.application import service, internet


class MapResolver(client.Resolver):
    def __init__(self, mapping, servers):
        client.Resolver.__init__(self, servers=servers)

        self.mapping = mapping
        self.ttl = 10

    def lookupAddress(self, name, timeout = None):
        if name in self.mapping:
            # We know the answer.
            value = self.mapping[name]
            return [
                (
                    dns.RRHeader(
                        name, dns.A, dns.IN, self.ttl,
                        dns.Record_A(value, self.ttl)
                    ),
                ),
                (),
                ()
            ]
        else:
            # Ask our backend server.
            return self._lookup(name, dns.IN, dns.A, timeout)


class CustomMapping(Mapping):
    def __init__(self, servers):
        self._servers = servers

    def __getitem__(self, key):
        return self._servers[key]

    def __iter__(self):
        return self._servers.iterkeys()

    def __len__(self):
        return len(self._servers)


# Our custom resolver.
custom_mapping = CustomMapping({"example.com": "33.33.33.33"})

# Upstream DNS server.
upstream_dns = "8.8.8.8"

# Setup Twisted application.
application = service.Application('dnsserver', 1, 1)
simpledns = MapResolver(custom_mapping, servers=[(upstream_dns, 53)])

# Create protocols.
f = server.DNSServerFactory(caches=[cache.CacheResolver()], clients=[simpledns])
p = dns.DNSDatagramProtocol(f)
f.noisy = p.noisy = False

# Register both TCP and UDP on port 53.
ret = service.MultiService()
PORT = 53

# Attach services to the parent.
for (klass, arg) in [(internet.TCPServer, f), (internet.UDPServer, p)]:
    s = klass(PORT, arg)
    s.setServiceParent(ret)

# Run as a twistd application.
ret.setServiceParent(service.IServiceCollection(application))

if __name__ == '__main__':
    import sys
    print "Usage: twistd -ny %s" % sys.argv[0]
