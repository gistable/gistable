#!/bin/python2.7
# -`*- coding: utf-8 -*-

"""
test for Server-Side events in flask

inspiration from:
http://www.html5rocks.com/en/tutorials/eventsource/basics/
https://github.com/niwibe/sse.git
https://github.com/niwibe/django-sse.git
https://github.com/jkbr/chat
"""

from __future__ import unicode_literals
import time
import sys
from flask import Response
from flask.views import View


class Sse(object):
    def __init__(self):
        self._buffer = {}
        self._buffer['messages'] = {}

    def set_retry(self, num):
        self._buffer['retry'] = num

    def set_event_id(self, event_id):
        self._buffer['id'] = event_id

    def reset_event_id(self):
        self.set_event_id(None)

    def _parse_text(self, text, encoding='utf-8'):
        if isinstance(text, (list, tuple, set)):
            text = ''.join(self._parse_text(i) for i in text)

        if isinstance(text, bytes):
            text = text.decode(encoding)

        return str(text) + '\n'

    def add_message(self, text, event='message'):
        """
        Add message with eventname to the buffer.
        """
        event_list = self._buffer['messages'].setdefault(event, [])
        event_list.append(self._parse_text(text))

    def __str__(self):
        if sys.version_info[0] >= 3:  # Python 3
            return self.__unicode__()
        return self.__unicode__().encode('utf8')

    def __unicode__(self):
        return ''.join(i for i in self)

    def flush(self):
        """
        Reset the internal buffer to initial state.
        """
        self._buffer.clear()
        self._buffer['messages'] = {}

    def __iter__(self):
        if 'retry' in self._buffer:
            yield "retry: {0}\n\n".format(self._buffer['retry'])

        if 'id' in self._buffer:
            if self._buffer['id']:
                yield "id: {0}\n\n".format(self._buffer['id'])
            else:
                yield "id\n\n"  # Reset event id

        for eventname in self._buffer['messages']:
            for message in self._buffer['messages'][eventname]:
                yield "event: {0}\n".format(eventname)
                yield "data: {0}\n".format(message)


class SseStream(View):
    def get_last_id(self):
        if "HTTP_LAST_EVENT_ID" in self.request.META:
            return self.request.META['HTTP_LAST_EVENT_ID']
        return None

    def _compose_message():
        raise NotImplementedError

    def _iterator(self):
        while self._compose_message():
            for line in self.sse:
                yield line
            self.sse.flush()

    def dispatch_request(self):
        self.sse = Sse()
        response = Response(self._iterator(), mimetype="text/event-stream")
        return response


class PeriodicStream(SseStream):
    def __init__(self, functions):
        self.functions = functions
        self.counter = 0

    def _compose_message(self):
        time.sleep(0.1)
        self.counter += 1
        if self.counter > 600:
            self.counter = 0
        for freq, func in self.functions.values():
            if self.counter % freq == 0:
                func(self, freq)
        return True


class RedisSseStream(SseStream):
    def __init__(self, handlers, pubsub):
        self.handlers = handlers
        pubsub.subscribe('stream')
        self._messages = pubsub.listen()

    def _compose_message(self):
        message = self._messages.next()['data']
        if message in self.handlers.keys():
            self.handlers[message](self)
        return True
