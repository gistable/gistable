# Fire this using gunicorn falcon_gevent_streaming
# and head to 127.0.0.1:8000 in a browser.
# Requirements:
# pip install falcon gevent

import falcon

import gevent

from gevent.queue import Queue
from gevent.event import Event

application = falcon.API()


def do_work(q, start=0, end=12, wait=0, wait_each=0, color='black'):
    if wait:
        gevent.sleep(wait)
    for i in xrange(start, end):
        if wait_each:
            gevent.sleep(wait_each)
        q.put('<span style="color: {};">{}</span> '.format(color, i))


def finish_when_ready(ev, q):
    ev.wait()
    q.put(StopIteration)


def finish_after(ev, after):
    gevent.sleep(after)
    ev.set()


class Thing:
    def on_get(self, req, resp):
        q = Queue()
        e = Event()
        q.put(' ' * 1024)
        gevent.spawn(do_work, q, start=2, end=10, wait=3, color='red')
        gevent.spawn(do_work, q, wait_each=1, color='green')
        gevent.spawn(do_work, q, wait=5, wait_each=0.25, color='blue')
        gevent.spawn(finish_when_ready, e, q)
        gevent.spawn(finish_after, e, 15)
        resp.content_type = 'text/html'
        resp.stream = q


things = Thing()

application.add_route('/', things)
