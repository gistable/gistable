"""Implementation of pycurl's "easy" interface that uses pycurl's multi interface + gevent.
"""
# parts of code from Tornado's curl_httpclient.py
import logging
import gevent
assert gevent.version_info[:2] >= (0, 14), 'Gevent 0.14 or older required. Your version is %s' % gevent.__version__
from gevent.core import EVENTS, READ, WRITE
from gevent.hub import Waiter


pycurl = __import__('pycurl')
for key, value in pycurl.__dict__.iteritems():
    if not key.startswith('_'):
        key = {'Curl': '_Curl'}.get(key, key)
        globals()[key] = value


class GeventCurl(object):
    """Integrate Curl's Multi interface into gevent's loop."""
    # QQQ cannot inherit from CurlMulti for some reason

    def __init__(self, loop=None):
        if loop is None:
            loop = gevent.get_hub().loop
        self.loop = loop
        self._watchers = {}
        self._timeout = None
        self._obj = CurlMulti()
        self.setopt(pycurl.M_TIMERFUNCTION, self._set_timeout)
        self.setopt(pycurl.M_SOCKETFUNCTION, self._set_socket)
        try:
            self._socket_action = self._obj.socket_action
        except AttributeError:
            # socket_action is found in pycurl since 7.18.2 (it's been
            # in libcurl longer than that but wasn't accessible to
            # python).
            logging.warning("socket_action method missing from pycurl; "
                            "falling back to socket_all. Upgrading "
                            "libcurl and pycurl will improve performance")
            self._socket_action = \
                lambda fd, action: self._obj.socket_all()

    def __getattr__(self, item):
        return getattr(self._obj, item)

    def _set_timeout(self, msecs):
        """Called by libcurl to schedule a timeout."""
        if self._timeout is not None:
            self._timeout.stop()
        self._timeout = self.loop.timer(msecs)
        self._timeout.start(self._handle_timeout)

    def add_handle(self, curl):
        curl = getattr(curl, '_obj', curl)
        self._obj.add_handle(curl)
        self._set_timeout(0)

    def remove_handle(self, curl):
        curl = getattr(curl, '_obj', curl)
        self._obj.remove_handle(curl)

    def _set_socket(self, event, fd, multi, data):
        """Called by libcurl when it wants to change the file descriptors it cares about."""
        # pycurl's event happen to match libev's event
        if event == pycurl.POLL_REMOVE or not event:
            watcher = self._watchers.pop(fd, None)
            if watcher is not None:
                watcher.stop()
        else:
            watcher = self._watchers.get(fd)
            if watcher is None:
                watcher = self.loop.io(fd, event)
                watcher.start(self._handle_events, EVENTS, fd)
                self._watchers[fd] = watcher
            else:
                if watcher.events != event:
                    watcher.stop()
                    watcher.events = event
                    watcher.start(self._handle_events, EVENTS, fd)

    def _handle_timeout(self):
        """Called by IOLoop when the requested timeout has passed."""
        if self._timeout is not None:
            self._timeout.stop()
            self._timeout = None
        while True:
            try:
                ret, num_handles = self._obj.socket_action(pycurl.SOCKET_TIMEOUT, 0)
            except pycurl.error, e:
                ret = e.args[0]
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        self._finish_pending_requests()

        # In theory, we shouldn't have to do this because curl will
        # call _set_timeout whenever the timeout changes. However,
        # sometimes after _handle_timeout we will need to reschedule
        # immediately even though nothing has changed from curl's
        # perspective. This is because when socket_action is
        # called with SOCKET_TIMEOUT, libcurl decides internally which
        # timeouts need to be processed by using a monotonic clock
        # (where available) while tornado uses python's time.time()
        # to decide when timeouts have occurred. When those clocks
        # disagree on elapsed time (as they will whenever there is an
        # NTP adjustment), tornado might call _handle_timeout before
        # libcurl is ready. After each timeout, resync the scheduled
        # timeout with libcurl's current state.
        new_timeout = self._obj.timeout()
        if new_timeout != -1:
            self._set_timeout(new_timeout)

    def _handle_events(self, events, fd):
        action = 0
        if events & READ:
            action |= pycurl.CSELECT_IN
        if events & WRITE:
            action |= pycurl.CSELECT_OUT
        while True:
            try:
                ret, num_handles = self._socket_action(fd, action)
            except pycurl.error, e:
                ret = e.args[0]
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        self._finish_pending_requests()

    def _finish_pending_requests(self):
        """Process any requests that were completed by the lastcall to multi.socket_action."""
        while True:
            num_q, ok_list, err_list = self._obj.info_read()
            for curl in ok_list:
                curl.waiter.switch()
            for curl, errnum, errmsg in err_list:
                curl.waiter.throw(Exception('%s %s' % (errnum, errmsg)))
            if num_q == 0:
                break


class cached_class_property(object):

    def __init__(self, func, name=None, doc=None):
        name = name or func.__name__
        self.__name__ = '_cached_class_property_' + name
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, _obj, cls, _missing=object()):
        value = getattr(cls, self.__name__, _missing)
        if value is _missing:
            value = self.func(cls)
            setattr(cls, self.__name__, value)
        return value


class Curl(object):

    _multi_class = GeventCurl

    @cached_class_property  # should be threadlocal_cached_class_property XXX
    def _multi(cls):
        return cls._multi_class()

    def __init__(self):
        self._obj = _Curl()

    def __getattr__(self, item):
        return getattr(self._obj, item)

    def perform(self):
        assert getattr(self._obj, 'waiter', None) is None, 'This curl object is already used by another greenlet'
        waiter = self._obj.waiter = Waiter()
        try:
            self._multi.add_handle(self)
            try:
                return waiter.get()
            finally:
                self._multi.remove_handle(self)
        finally:
            del self._obj.waiter
