# Autobahn client with auto-reconnect capability
# Totally based on https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/client.py

import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted import wamp, websocket
from autobahn.wamp import types


class MyFrontendComponent(wamp.ApplicationSession):
    # TODO: coding fun :)
    def onJoin(self, details):
        pass

    def onDisconnect(self):
        pass


class MyClientFactory(websocket.WampWebSocketClientFactory, ReconnectingClientFactory):
    maxDelay = 30

    def clientConnectionFailed(self, connector, reason):
        print "*************************************"
        print "Connection Failed"
        print "reason:", reason
        print "*************************************"
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        print "*************************************"
        print "Connection Lost"
        print "reason:", reason
        print "*************************************"
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


if __name__ == '__main__':
    ## 0) start logging to console
    log.startLogging(sys.stdout)

    ## 1) create a WAMP application session factory
    component_config = types.ComponentConfig(realm = "realm1")
    session_factory = wamp.ApplicationSessionFactory(config = component_config)
    session_factory.session = MyFrontendComponent

    ## 2) create a WAMP-over-WebSocket transport client factory
    transport_factory = MyClientFactory(session_factory)

    ## 3) start the client from a Twisted endpoint
    transport_factory.host = 'localhost'
    transport_factory.port = 8080
    websocket.connectWS(transport_factory)

    ## 4) now enter the Twisted reactor loop
    reactor.run()
