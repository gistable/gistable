from twisted.web.iweb import IBodyProducer
from twisted.internet import defer
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
import urllib

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

def httpRequest(url, values={}, headers={}, method='POST'):
    # Construct an Agent.
    agent = Agent(reactor)
    data = urllib.urlencode(values)

    d = agent.request(method,
                      url,
                      Headers(headers),
                      StringProducer(data) if data else None)

    def handle_response(response):
        if response.code == 204:
            d = defer.succeed('')
        else:
            class SimpleReceiver(protocol.Protocol):
                def __init__(s, d):
                    s.buf = ''; s.d = d
                def dataReceived(s, data):
                    s.buf += data
                def connectionLost(s, reason):
                    # TODO: test if reason is twisted.web.client.ResponseDone, if not, do an errback
                    s.d.callback(s.buf)

            d = defer.Deferred()
            response.deliverBody(SimpleReceiver(d))
        return d

    d.addCallback(handle_response)
    return d

# Sample usage:

d = httpRequest(
    "http://...",                            
    {   
        'query_arg': 'value',          
    },
    headers={'Content-Type': ['application/x-www-form-urlencoded']}                      
)
