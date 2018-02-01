
import datetime
import functools
import logging
import os
import time

import gobject
import gtk

from tornado import ioloop
from tornado.log import gen_log


class GtkIOLoop(ioloop.IOLoop):
    READ = gobject.IO_IN
    WRITE = gobject.IO_OUT
    ERROR = gobject.IO_ERR | gobject.IO_HUP

    def initialize(self, time_func=None):
        super(GtkIOLoop, self).initialize()
        self.time_func = time_func or time.time
        self._handles = {}

    def close(self, all_fds=False):
        if all_fds:
            for fd in self._handles.keys():
                try:
                    os.close(fd)
                except Exception:
                    gen_log.debug("error closing fd %s", fd, exc_info=True)

    def _handle_events(self, fd, events, callback):
        callback(fd, events)
        return True

    def add_handler(self, fd, callback, events):
        handle = gobject.io_add_watch(
            fd, events | self.ERROR, self._handle_events, callback)
        self._handles[fd] = handle, callback

    def update_handler(self, fd, events):
        handle, callback = self._handles.pop(fd)
        gobject.source_remove(handle)
        self.add_handler(fd, callback, events)

    def remove_handler(self, fd):
        handle, _ = self._handles.pop(fd)
        gobject.source_remove(handle)

    def start(self):
        if not logging.getLogger().handlers:  # pragma: no cover
            logging.basicConfig()
        gtk.main()

    def stop(self):
        gtk.main_quit()

    def time(self):
        return self.time_func()

    def add_timeout(self, deadline, callback):
        if isinstance(deadline, datetime.timedelta):  # pragma: no cover
            seconds = ioloop._Timeout.timedelta_to_seconds(deadline)
        else:
            seconds = deadline - self.time()
        ms = max(0, int(seconds * 1000))
        handle = gobject.timeout_add(ms, self._run_callback, callback)
        return handle

    def remove_timeout(self, handle):
        gobject.source_remove(handle)

    def add_callback(self, callback, *args, **kwargs):
        callback = functools.partial(callback, *args, **kwargs)
        gobject.timeout_add(0, self._run_callback, callback)

    add_callback_from_signal = add_callback
