"""
An XPUB/XSUB broker that forwards subscriptions

"""
import os
import string
import sys
import time
from random import randint
from threading import Thread

import zmq

xpub_url = "tcp://127.0.0.1:5555"
xsub_url = "tcp://127.0.0.1:5556"

def broker(ctx):
    xpub = ctx.socket(zmq.XPUB)
    xpub.bind(xpub_url)
    xsub = ctx.socket(zmq.XSUB)
    xsub.bind(xsub_url)
    
    poller = zmq.Poller()
    poller.register(xpub, zmq.POLLIN)
    poller.register(xsub, zmq.POLLIN)
    while True:
        events = dict(poller.poll(1000))
        if xpub in events:
            message = xpub.recv_multipart()
            print "[BROKER] subscription message: %r" % message[0]
            xsub.send_multipart(message)
        if xsub in events:
            message = xsub.recv_multipart()
            # print "publishing message: %r" % message
            xpub.send_multipart(message)


def publisher(ctx):
    pub = ctx.socket(zmq.PUB)
    pub.connect(xsub_url)
    # pub.bind(xpub_url)
    for n in range(1000):
        for topic in "ABC":
            msg = [topic, str(n)]
            pub.send_multipart(msg)
        time.sleep(0.25)


def subscriber(ctx):
    sub = ctx.socket(zmq.SUB)
    sub.connect(xpub_url)
    topics = 'ABC'
    subscription = set()
    while True:
        r = randint(0,len(topics))
        if r < len(topics):
            topic = topics[r]
            if topic not in subscription:
                subscription.add(topic)
                sub.setsockopt(zmq.SUBSCRIBE, topic)
        r2 = randint(0,len(topics))
        if r2 != r and r2 < len(topics):
            topic = topics[r2]
            if topic in subscription:
                subscription.remove(topic)
                sub.setsockopt(zmq.UNSUBSCRIBE, topic)
        time.sleep(0.3)
        print "subscribed to: %r" % sorted(subscription)
        while True:
            if sub.poll(timeout=0):
                print "received", sub.recv_multipart()
            else:
                break

if __name__ == '__main__':
    ctx = zmq.Context()
    threads = [ Thread(target=f, args=(ctx,)) for f in (broker, publisher, subscriber) ]
    [ t.start() for t in threads ]
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    "terminating"
    ctx.term()
    [ t.join() for t in threads ]

