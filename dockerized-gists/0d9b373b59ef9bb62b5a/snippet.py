#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

"""
Watch for new downloads in ~/Downloads (or another directory) and take actions.
The actions are determined by the file extension (determining the mime type).
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
import os
import subprocess
import syslog

import blinker
import inotifyx


class InotifyWatcher(object):
    """Watch for new, complete file creations."""
    created = blinker.Signal()

    def __init__(self):
        self._fd = inotifyx.init()
        self._watches = {}
        self._starts = {}
        syslog.openlog(b"InotifyWatcher")

    def add_watch(self, directory):
        thedir = os.path.expanduser(os.path.expandvars(directory))
        wd = inotifyx.add_watch(self._fd, os.path.expandvars(thedir),
                                inotifyx.IN_CREATE | inotifyx.IN_CLOSE_WRITE)
        self._watches[wd] = thedir
        return wd

    def __del__(self):
        self.close()

    def close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
            self._watches.clear()
            syslog.closelog()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def run(self):
        while 1:
            try:
                events = inotifyx.get_events(self._fd)
            except KeyboardInterrupt:
                break
            for event in events:
                if event.mask & inotifyx.IN_CREATE:
                    self._starts[event.wd] = event.name
                elif event.mask & inotifyx.IN_CLOSE_WRITE:
                    name = self._starts.pop(event.wd, None)
                    if name is not None:
                        thedir = self._watches[event.wd]
                        syslog.syslog(
                            "created {!r}".format(name).encode("ascii"))
                        InotifyWatcher.created.send(self, path=os.path.join(thedir, name))


def open_file(watcher, path=None):
    subprocess.call(["xdg-open", path])


def main(argv):
    InotifyWatcher.created.connect(open_file)
    thedir = argv[1] if len(argv) > 1 else "~/Downloads"
    with InotifyWatcher() as watcher:
        watcher.add_watch(thedir)
        watcher.run()


main(sys.argv)
