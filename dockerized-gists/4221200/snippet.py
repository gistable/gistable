#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()  # Patch everything
import gevent
import time


class Hub(object):
    """A simple reactor hub... In async!"""

    def __init__(self, name=None):
        self.name = name
        self.handlers = {}

    def on(self, event_name, handler):
        """Binds an event to a function."""
        handlers = self.handlers.get(event_name, [])
        if not handler in handlers:
            handlers.append(handler)
            self.handlers[event_name] = handlers

    def off(self, event_name, handler):
        """Unbinds an event to a function."""
        handlers = self.handlers.get(event_name, [])
        handlers.remove(handler)

    def emit(self, event_name, *args, **kwargs):
        """Calls an event. You can also pass arguments."""
        handlers = self.handlers.get(event_name, [])
        for handler in handlers:
            # XXX: If spawned within a greenlet, there's no need to join
            # the greenlet. It is automatically executed.
            gevent.spawn(handler, *args, **kwargs)

    def start(self, *entry_points):
        """Run entry point."""
        gevent.joinall([gevent.spawn(ep) for ep in entry_points])


##
#
# Usage...
#
# Here's an example that uses redis' pub/sub feature.
##

import redis

# Create an instance of the hub.
hub = Hub(name='myhub')
# Create a redis instance
r = redis.Redis()


def emojify(string):
    # Let's say that this is a long process.
    time.sleep(5)
    print "Emojifies: :%s:" % string


def hello(string):
    # A slightly long process.
    time.sleep(1)
    print "Says hello: Hello, %s" % string


# You can bind multiple events.
hub.on('name.awesome', emojify)
hub.on('name.awesome', hello)


# More events.
def capitalize_then_proceed(string):
    print "Capitalize: %s" % string.upper()
    # You can also emit more events
    hub.emit('name.awesome', string)


hub.on('name.only_me', capitalize_then_proceed)


def entry_point():
    ps = r.pubsub()
    ps.subscribe(['awesome'])
    for message in ps.listen():
        if message['type'] == 'message':
            print "# Before events."
            if message['data'].lower() != 'jesse':
                hub.emit('name.awesome', message['data'])
            else:
                hub.emit('name.only_me', message['data'])
            print "# Should be after events but it happens in async!"


if __name__ == '__main__':
    print "Running awesome!"
    hub.start(entry_point)
