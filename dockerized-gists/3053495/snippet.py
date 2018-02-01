"""
realertime.lib.spawn
~~~~~~~~~~~~~~~~~~~~

:author: Adam Hitchcock
:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

from functools import partial
from gevent import Greenlet
from gevent.hub import get_hub
from pprint import pformat
import logging
import time

logger = logging.getLogger(__name__)


def _failhard(message, func, greenlet, *args, **kwargs):
    try:
        line = "-" * 80
        msg = """
        %(line)s
        %(func)s
        ** %(message)s **

        %(greenlet)s is dead

        args:
            %(args)s

        kwargs:
            %(kwargs)s

        %(line)s"""

        fmt = {
        'line': line,
        'func': func.__name__ if hasattr(func, '__name__') else func,
        'message': message,
        'greenlet': greenlet,
        'args': pformat(args),
        'kwargs': pformat(kwargs),
        }

        logger.critical(msg % fmt)

        logger.exception(greenlet.exception)

        # TODO: gevent 1.0 will allow a simple sys.exit(message)
    except Exception, e:
        logger.exception(e)
    finally:

        get_hub().parent.throw(SystemExit())


class TimeSensitiveBackoff(object):
    """
    Iterator which yields values until finished like normal, however will reset
    itself (and start yielding from the beginning) if a value hasn't been
    requested from the iterator in the "healthy_threshold" amount of time
    (defaults to 5 minutes).
    """

    healthy_threshold = 60 * 5  # 5 minutes

    def __init__(self, sequence=None):
        if not sequence:
            sequence = (2 ** i / 1000.0 for i in xrange(15))

        self.sequence = list(sequence)
        self.last_next = time.time()
        self.__reset_iterator()

    def next(self):
        time_since_last_iteration = (time.time() - self.last_next)

        if time_since_last_iteration > self.healthy_threshold:
            self.__reset_iterator()

        self.last_next = time.time()
        return self.iterator.next()

    def __iter__(self):
        return self

    def __reset_iterator(self):
        self.iterator = iter(self.sequence)


class Watchdog(object):
    """
    Runs a callable in a gevent greenlet, and restarts the greenlet with the
    same callable iff any exception is raised from the greenlet.  Uses
    exponential backoff to respawn the greenlet until eventually it gives up.
    """

    def __init__(self, func, backoff=None):
        if not callable(func):
            raise ValueError('Func argument is not callable')

        if not backoff:
            backoff = TimeSensitiveBackoff()

        self.func = func
        self.backoff = backoff

    def __call__(self, greenlet):
        try:
            logger.exception(greenlet.exception)
            time.sleep(self.backoff.next())
            greenlet = self.respawn()
            return greenlet
        except StopIteration:
            _failhard('backoff exceeded', self.func, greenlet)
            get_hub().parent.throw(SystemExit())

    def spawn(self):
        self.greenlet = Greenlet(self.func)
        self.greenlet.link_exception(self)
        self.greenlet.start()
        return self.greenlet

    def respawn(self):
        return self.spawn()


def _spawn_with_linktype_callback(link_func, callback, func, *args, **kwargs):
    if link_func not in ('link', 'link_exception', 'link_value'):
        raise Exception('link_func %s is not a valid link type' % link_func)

    g = Greenlet(func, *args, **kwargs)
    getattr(g, link_func)(callback)
    g.start()
    return g


def _spawn_with_linktype_failhard(link_func, func, message, *args, **kwargs):
    callback = partial(_failhard, message, func)
    return _spawn_with_linktype_callback(link_func, callback, func, *args, **kwargs)


def spawn_with_exception_failhard(message, func, *args, **kwargs):
    """
    Will cause the process to exit iff the spawned greenlet exits with an
    exception. A return statement will not cause the exit.

    :param message: The message to display on exit
    :param func: The function to spawn with the greenlet
    :param *args: The args to pass to the greenlet
    :param **kwargs: The kwargs to pass to the greenlet
    """

    return _spawn_with_linktype_failhard('link_exception', func, message, *args, **kwargs)


def spawn_with_watchdog(func, *args):
        watchdog = Watchdog(partial(func, *args))

        #TODO: return a generator of greenlets for future spawnings
        return watchdog.spawn()