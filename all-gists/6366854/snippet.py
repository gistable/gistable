from twisted.internet import reactor, defer
from twisted.web.http import HTTPChannel
from twisted.application import internet, service
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource

class SlowResource(Resource):
    isLeaf = True
    waiting_requests = []

    def notify_no_more_waiting(self):
        if not self.waiting_requests:
            return defer.succeed(None)
        return defer.gatherResults(self.waiting_requests, consumeErrors=True) \
                .addBoth(lambda ign: None)

    def write_result(self, request):
        request.write('{}')
        request.finish()

    def render_GET(self, request):
        reactor.callLater(5, self.write_result, request)
        d = request.channel.notifyConnectionLost()
        self.waiting_requests.append(d)
        d.addBoth(lambda ign: self.waiting_requests.remove(d))
        return NOT_DONE_YET


class MyProtocol(HTTPChannel):
    _connection_lost = defer.succeed(None)

    def notifyConnectionLost(self):
        return self._connection_lost

    def connectionMade(self):
        HTTPChannel.connectionMade(self)
        self._connection_lost = defer.Deferred()

    def connectionLost(self, reason):
        HTTPChannel.connectionLost(self, reason)
        self._connection_lost.callback(None)

slow_resource = SlowResource()
site = Site(slow_resource)
site.protocol = MyProtocol
application = service.Application("MyApp")
server = internet.TCPServer(8080, site)
server.setServiceParent(application)

@defer.inlineCallbacks
def graceful_shutdown():
    yield server.stopService()
    yield slow_resource.notify_no_more_waiting()

reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)