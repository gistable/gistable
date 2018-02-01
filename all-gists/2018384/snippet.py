from twisted.web import http
from twisted.internet import protocol, reactor

from twisted.internet.error import CannotListenError, ConnectError
from twisted.internet.interfaces import IReactorTCP
from zope.interface import implements

from twisted.python import log

class ProxyConnectError(ConnectError):
    pass

class HTTPProxyConnector(object):
    implements(IReactorTCP)

    def __init__(self, proxy_host, proxy_port,
                 reactor=reactor):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.reactor = reactor

    def listenTCP(port, factory, backlog=50, interface=''):
        raise CannotListenError("Cannot BIND via HTTP proxies")

    def connectTCP(self, host, port, factory, timeout=30, bindAddress=None):
        f = HTTPProxiedClientFactory(factory, host, port)
        self.reactor.connectTCP(self.proxy_host,
                                self.proxy_port,
                                f, timeout, bindAddress)


class HTTPProxiedClientFactory(protocol.ClientFactory):
    def __init__(self, delegate, dst_host, dst_port):
        self.delegate = delegate
        self.dst_host = dst_host
        self.dst_port = dst_port

    def startedConnecting(self, connector):
        return self.delegate.startedConnecting(connector)

    def buildProtocol(self, addr):
        p = HTTPConnectTunneler(self.dst_host, self.dst_port, addr)
        p.factory = self
        return p

    def clientConnectionFailed(self, connector, reason):
        return self.delegate.clientConnectionFailed(connector, reason)

    def clientConnectionLost(self, connector, reason):
        return self.delegate.clientConnectionLost(connector, reason)


class HTTPConnectTunneler(protocol.Protocol):
    http = None
    otherConn = None
    noisy = True

    def __init__(self, host, port, orig_addr):
        self.host = host
        self.port = port
        self.orig_addr = orig_addr

    def connectionMade(self):
        self.http = HTTPConnectSetup(self.host, self.port)
        self.http.parent = self
        self.http.makeConnection(self.transport)

    def connectionLost(self, reason):
        if self.noisy:
            log.msg("HTTPConnectTunneler connectionLost", reason)

        if self.otherConn is not None:
            self.otherConn.connectionLost(reason)
        if self.http is not None:
            self.http.connectionLost(reason)

    def proxyConnected(self):
        self.otherConn = self.factory.delegate.buildProtocol(self.orig_addr)
        self.otherConn.makeConnection(self.transport)

        # Get any pending data from the http buf and forward it to otherConn
        buf = self.http.clearLineBuffer()
        if buf:
            self.otherConn.dataReceived(buf)

    def dataReceived(self, data):
        if self.otherConn is not None:
            if self.noisy:
                log.msg("%d bytes for otherConn %s" %
                        (len(data), self.otherConn))
            return self.otherConn.dataReceived(data)
        elif self.http is not None:
            if self.noisy:
                log.msg("%d bytes for proxy %s" %
                        (len(data), self.otherConn))
            return self.http.dataReceived(data)
        else:
            raise Exception("No handler for received data... :(")


class HTTPConnectSetup(http.HTTPClient):
    noisy = True

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connectionMade(self):
        self.sendCommand('CONNECT', '%s:%d' % (self.host, self.port))
        self.endHeaders()

    def handleStatus(self, version, status, message):
        if self.noisy:
            log.msg("Got Status :: %s %s %s" % (status, message, version))
        if str(status) != "200":
            raise ProxyConnectError("Unexpected status on CONNECT: %s" % status)

    def handleHeader(self, key, val):
        if self.noisy:
            log.msg("Got Header :: %s: %s" % (key, val))

    def handleEndHeaders(self):
        if self.noisy:
            log.msg("End Headers")
        self.parent.proxyConnected()

    def handleResponse(self, body):
        if self.noisy:
            log.msg("Got Response :: %s" % (body))


if __name__ == '__main__':
    import sys

    log.startLogging(sys.stderr)

    factory = MySSHClientFactory()
    proxy = HTTPProxyConnector('myproxy.server', 8080)
    proxy.connectTCP('mybackend.server', 22, factory)
    reactor.run()