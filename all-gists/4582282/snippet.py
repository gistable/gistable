"""Proof of concept tornado/tulip integration.

Works with the current development branch of both projects as of
Jan 20.  Current status:  The tornado test suite passes cleanly
on a tulip-backed IOLoop.  The tornado-backed event loop for tulip
supports the core call_later and add_reader method families, but not
the higher-level networking methods.

To run the tornado test suite on tulip, make sure both projects
and this file are on your python path and run:
  python3.3 -m tornado.test.runtests --ioloop=tornado_tulip.TulipIOLoop

To run the tulip event loop test suite on tornado (still very
incomplete with many tests failing or skipped):
  python3.3 tornado_tulip.py
"""

import datetime
import functools
import os

import tulip.events

from tornado.ioloop import IOLoop
from tornado import stack_context

class TulipIOLoop(IOLoop):
    def initialize(self):
        self.tulip_loop = tulip.events.new_event_loop()
        # Maps fd to handler function (as in IOLoop.add_handler)
        self.handlers = {}
        # Maps fd to reader/writer tulip.events.Handler objects
        self.readers = {}
        self.writers = {}
        self.closing = False

    def close(self, all_fds=False):
        self.closing = True
        for fd in list(self.handlers):
            self.remove_handler(fd)
            if all_fds:
                os.close(fd)
        self.tulip_loop.close()

    def add_handler(self, fd, handler, events):
        if fd in self.handlers:
            raise ValueError("fd %d added twice" % fd)
        self.handlers[fd] = stack_context.wrap(handler)
        if events & IOLoop.READ:
            self.readers[fd] = self.tulip_loop.add_reader(
                fd, self._handle_events, fd, IOLoop.READ)
        if events & IOLoop.WRITE:
            self.writers[fd] = self.tulip_loop.add_writer(
                fd, self._handle_events, fd, IOLoop.WRITE)

    def update_handler(self, fd, events):
        if events & IOLoop.READ:
            if fd not in self.readers:
                self.readers[fd] = self.tulip_loop.add_reader(
                    fd, self._handle_events, fd, IOLoop.READ)
        else:
            if fd in self.readers:
                self.tulip_loop.remove_reader(fd)
                self.readers.pop(fd).cancel()
        if events & IOLoop.WRITE:
            if fd not in self.writers:
                self.writers[fd] = self.tulip_loop.add_writer(
                    fd, self._handle_events, fd, IOLoop.WRITE)
        else:
            if fd in self.writers:
                self.tulip_loop.remove_writer(fd)
                self.writers.pop(fd).cancel()

    def remove_handler(self, fd):
        if fd not in self.handlers:
            return
        if fd in self.readers:
            self.tulip_loop.remove_reader(fd)
            self.readers.pop(fd).cancel()
        if fd in self.writers:
            self.tulip_loop.remove_writer(fd)
            self.writers.pop(fd).cancel()
        del self.handlers[fd]

    def _handle_events(self, fd, events):
        try:
            self.handlers[fd](fd, events)
        except KeyError:
            print(fd, events)
            print('read', IOLoop.READ)
            import traceback
            print(''.join(traceback.format_stack()))
            raise

    def start(self):
        self.tulip_loop.run_forever()

    def stop(self):
        self.tulip_loop.stop()

    def _run_callback(self, callback, *args, **kwargs):
        try:
            callback(*args, **kwargs)
        except Exception:
            self.handle_callback_exception(callback)

    def add_timeout(self, deadline, callback):
        if isinstance(deadline, (int, float)):
            delay = max(deadline - self.time(), 0)
        elif isinstance(deadline, datetime.timedelta):
            delay = deadline.total_seconds()
        else:
            raise TypeError("Unsupported deadline %r", deadline)
        return self.tulip_loop.call_later(delay, self._run_callback,
                                          stack_context.wrap(callback))

    def remove_timeout(self, timeout):
        timeout.cancel()

    def add_callback(self, callback, *args, **kwargs):
        if self.closing:
            raise RuntimeError("IOLoop is closing")
        if kwargs:
            self.tulip_loop.call_soon_threadsafe(functools.partial(
                    self._run_callback, stack_context.wrap(callback),
                    *args, **kwargs))
        else:
            self.tulip_loop.call_soon_threadsafe(
                self._run_callback, stack_context.wrap(callback), *args)

    add_callback_from_signal = add_callback


class TornadoEventLoop(tulip.events.EventLoop):
    def __init__(self, io_loop=None):
        self.io_loop = io_loop or IOLoop()
        self.running_until_idle = False
        self.fds = {}

    def run(self):
        self.running_until_idle = True
        self.call_soon(lambda:None)
        self.io_loop.start()

    def stop(self):
        self.io_loop.stop()

    def close(self):
        self.io_loop.close()

    def call_later(self, delay, callback, *args):
        handler = tulip.events.make_handler(None, callback, args)
        self.io_loop.add_timeout(
            datetime.timedelta(seconds=delay),
            functools.partial(self._run_handler, handler))

    def call_repeatedly(self, interval, callback, *args):
        def wrapper():
            callback(*args)
            self.call_later(interval, wrapper)
        self.call_later(interval, wrapper)

    def call_soon(self, callback, *args):
        handler = tulip.events.make_handler(None, callback, args)
        self.io_loop.add_callback(functools.partial(self._run_handler, handler))
        return handler

    call_soon_threadsafe = call_soon

    def add_reader(self, fd, callback, *args):
        handler = tulip.events.make_handler(None, callback, args)
        if fd in self.fds:
            (_, writer) = self.fds[fd]
            self.fds[fd] = (handler, writer)
            self._io_loop.update_handler(fd, IOLoop.READ | IOLoop.WRITE)
        else:
            with stack_context.NullContext():
                self.fds[fd] = (handler, None)
                self.io_loop.add_handler(fd, self._handle_events, IOLoop.READ)
        return handler

    def remove_reader(self, fd):
        if fd not in self.fds:
            return False
        reader, writer = self.fds[fd]
        if reader is None:
            return False
        if writer is not None:
            self.fds[fd] = (None, writer)
            self.io_loop.update_handler(fd, IOLoop.WRITE)
        else:
            del self.fds[fd]
            self.io_loop.remove_handler(fd)
        return True

    def add_writer(self, fd, callback, *args):
        handler = tulip.events.make_handler(None, callback, args)
        if fd in self.fds:
            (reader, _) = self.fds[fd]
            self.fds[fd] = (reader, handler)
            self._io_loop.update_handler(fd, IOLoop.READ | IOLoop.WRITE)
        else:
            with stack_context.NullContext():
                self.fds[fd] = (None, handler)
                self.io_loop.add_handler(fd, self._handle_events, IOLoop.WRITE)
        return handler

    def remove_writer(self, fd):
        if fd not in self.fds:
            return False
        reader, writer = self.fds[fd]
        if writer is None:
            return False
        if reader is not None:
            self.fds[fd] = (reader, None)
            self.io_loop.update_handler(fd, IOLoop.READ)
        else:
            del self.fds[fd]
            self.io_loop.remove_handler(fd)
        return True

    def _handle_events(self, fd, events):
        reader, writer = self.fds[fd]
        if reader is not None and events & IOLoop.READ:
            if reader.cancelled:
                self.remove_reader(fd)
                self._stop_if_idle()
            else:
                self._run_handler(reader)
        if writer is not None and events & IOLoop.WRITE:
            if writer.cancelled:
                self.remove_writer(fd)
                self._stop_if_idle()
            else:
                self._run_handler(writer)

    def _run_handler(self, handler):
        if not handler.cancelled:
            handler.callback(*handler.args)
        self._stop_if_idle()

    def _stop_if_idle(self):
        if (self.running_until_idle and
            len(self.io_loop._handlers) <= 1 and  # don't count the waker pipe
            not self.io_loop._callbacks and
            not self.io_loop._timeouts):
            self.io_loop.stop()

    def create_connection(*args, **kw):
        raise unittest.SkipTest('not yet')

    def add_signal_handler(self, sig, callback, *args):
        raise unittest.SkipTest('not supported')

    def call_every_iteration(self, callback, *args):
        raise unittest.SkipTest('not supported')

if __name__ == '__main__':
    import tulip.events_test
    import unittest
    class TornadoEventLoopTests(tulip.events_test.EventLoopTestsMixin, unittest.TestCase):
        def setUp(self):
            self.event_loop = TornadoEventLoop()
            tulip.events.set_event_loop(self.event_loop)
    unittest.main()
