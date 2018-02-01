#!/usr/bin/env python

"""A Tornado example of RPC.

Designed to work with rpc_server.py as found in RabbitMQ Tutorial #6:
http://www.rabbitmq.com/tutorials/tutorial-six-python.html

Some code is borrowed from pika's tornado example.
"""

import platform
import os
import sys
import time
import uuid

import pika
import tornado.ioloop
import tornado.web

from pika.adapters.tornado_connection import TornadoConnection

__author__ = 'Brian McFadden'
__email__ = 'brimcfadden+gist.github.com@gmail.com'

HTML_HEADER = '<html><head><title>Tornado/Pika RPC</title></head><body>'
HTML_FOOTER = '</body></html>'

EXCHANGE = ''


class Fib(tornado.web.RequestHandler):
    """Uses an aysnchronous call to an RPC server to calculate fib(x).
    
    As with examples of asynchronous HTTP calls, this request will not finish
    until the remote response is received."""

    @tornado.web.asynchronous
    def get(self, number=''):

        if not number:
            self.redirect('/30')  # GET / --> GET /30

        self.number = number
        self.pika_client = self.application.settings.get('pika_client')
        self.mq_ch = self.pika_client.channel
        self.corr_id = str(uuid.uuid4())
        # Currently, one callback queue is made per request. Is mapping
        # responses in one queue to multiple RequestHandlers with a
        # correlation ID a better approach or not?
        self.queue_name = "{0}-{1}-{2}".format(platform.node(), os.getpid(),
                                               id(self))
        # Trying to bind to the nameless exchange breaks the program.
        callback = self.on_mq_declare if EXCHANGE else self.on_queue_bind
        self.mq_ch.queue_declare(exclusive=True, queue=self.queue_name,
                                 callback=callback)

    def on_mq_declare(self, frame):
        lg = "Queue {0} Declared. Now binding.".format(self.queue_name)
        pika.log.info(lg)
        self.mq_ch.queue_bind(exchange='', queue=self.queue_name,
                              callback=self.on_queue_bind)

    def on_queue_bind(self, frame):
        pika.log.info('Queue Bound. Issuing Basic Consume.')
        self.mq_ch.basic_consume(consumer_callback=self.on_rpc_response,
                                 queue=self.queue_name, no_ack=True)

        # After binding and listening to the queue with basic_consume,
        # publish the message.
        props = pika.BasicProperties(content_type='text/plain',
                                     delivery_mode=1,
                                     correlation_id=self.corr_id,
                                     reply_to=self.queue_name)
        pika.log.info('About to issue Basic Publish.')
        self.mq_ch.basic_publish(exchange='', routing_key='rpc_queue',
                                   body=str(self.number), properties=props,
                                   mandatory=1)

    def on_rpc_response(self, channel, method, header, body):
        lg = "RPC response: delivery tag #{0} | Body: {1}"
        pika.log.info(lg.format(method.delivery_tag, body))
        if header.correlation_id != self.corr_id:
            # I'm actually not sure what to do here yet.
            raise Exception('Someone dialed a wrong number.')

        # After the RPC response has been received, write to the browser.
        self.write(HTML_HEADER)
        self.write("fib({0}) = {1}".format(self.number, body))
        self.write(HTML_FOOTER)
        self.finish()


class PikaClient(object):
    """A modified class as described in pika's demo_tornado.py.
    It handles the connection for the Tornado instance. Messaging/RPC
    callbacks are handled by the Tornado RequestHandler above."""

    def __init__(self):
        self.connecting = False
        self.connection = None
        self.channel = None

    def connect(self):
        if self.connecting:
            pika.log.info('Already connecting to RabbitMQ.')
            return
        pika.log.info("Connecting to RabbitMQ")
        self.connecting = True
        creds = pika.PlainCredentials('guest', 'guest')
        params = pika.ConnectionParameters(host='localhost', port=5672,
                                           virtual_host='/', credentials=creds)
        self.connection = TornadoConnection(params,
                                            on_open_callback=self.on_connect)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connect(self, connection):
        self.connection = connection
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        pika.log.info('Channel Open')
        self.channel = channel
        # I'm having trouble using named exchanges.
        ## channel.exchange_declare(exchange='rpc_ex', type='direct',
        ##                          auto_delete=True, durable=False,
        ##                          callback=self.on_exchange_declare)

    def on_exchange_declare(self, frame):
        pika.log.info("Exchange declared.")

    def on_basic_cancel(self, frame):
        pika.log.info('Basic Cancel Ok.')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()


def main():
    pika.log.setup(color=True)
    pika_client = PikaClient()
    application = tornado.web.Application(
        [(r'/([0-9]*)', Fib)],
        **{'pika_client': pika_client, 'debug': True}
    )
    try:
        port = int(sys.argv[1])  # $ python tornadoweb_pika.py 80
    except:
        port = 8080
    application.listen(port)
    print "Tornado is serving on port {0}.".format(port)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_timeout(time.time() + .1, pika_client.connect)
    ioloop.start()

if __name__ == '__main__':
    main()
