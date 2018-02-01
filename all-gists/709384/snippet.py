#!/usr/bin/env python

from twisted.internet import reactor
from twisted.web import proxy, server
from twisted.web.resource import Resource

class ProxyResource(Resource):
    
    def getChild(self, path, request):
        request.received_headers['x-forwarded-host'] = request.received_headers['host']
        if path.startswith('live'):
            return proxy.ReverseProxyResource('localhost', 8090, '/live')
        return proxy.ReverseProxyResource('localhost', 8001, '/' + path)

if __name__ == '__main__':
    root = ProxyResource()
    reactor.listenTCP(8000, server.Site(root))
    reactor.run()