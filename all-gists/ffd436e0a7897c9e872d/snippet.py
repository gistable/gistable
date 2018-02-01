import pickle
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.python import log
 
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
 
import txamqp.spec
 
@inlineCallbacks
def gotConnection(conn, username, password):
    yield conn.authenticate(username, password)
    #print "Connected to broker."
 
    print "Authenticated. Ready to receive messages"
    chan = yield conn.channel(1)
    yield chan.channel_open()
 
    yield chan.queue_declare(queue="billingQueue")
 
    # Bind to routes
    yield chan.queue_bind(queue="billingQueue", exchange="billing", routing_key='bill_request.submit_sm_resp.*')
 
    yield chan.basic_consume(queue='billingQueue', no_ack=True, consumer_tag="billingFollower")
    queue = yield conn.queue("billingFollower")
  
    # Wait for messages
    # This can be done through a callback ...
    while True:
        msg = yield queue.get()

        print 'This is a bill with amount:%s for user:%s for sending msgid:%s' % (
        	msg.content.properties['headers']['amount'],
        	msg.content.properties['headers']['user-id'],
        	msg.content.properties['message-id']
        	)
 
    # A clean way to tear down and stop
    yield chan.basic_cancel("billingFollower")
    yield chan.channel_close()
    chan0 = yield conn.channel(0)
    yield chan0.connection_close()
 
    reactor.stop()
 
 
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5672
    vhost = '/'
    username = 'guest'
    password = 'guest'
    spec_file = '/etc/jasmin/resource/amqp0-9-1.xml'
 
    spec = txamqp.spec.load(spec_file)
 
    # Connect and authenticate
    d = ClientCreator(reactor,
        AMQClient,
        delegate=TwistedDelegate(),
        vhost=vhost,
        spec=spec).connectTCP(host, port)
    d.addCallback(gotConnection, username, password)
 
    def whoops(err):
        if reactor.running:
            log.err(err)
            reactor.stop()
 
    d.addErrback(whoops)
 
    reactor.run()