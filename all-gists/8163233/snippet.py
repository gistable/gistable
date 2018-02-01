#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Subclassing Observer for saving states of folders, and load this states at the next observation.

TODO : mapping events and handlers dispatching, for a shorter code.
"""
from __future__ import unicode_literals, print_function, division
import cPickle as pickle
import os

from watchdog.observers import Observer
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent


__author__ = "Serge Kilimoff-Goriatchkine"
__licence__ = 'MIT Licence'



class _EmptySnapshot(object):
    @property
    def stat_snapshot(self):
        return dict()

    @property
    def paths(self):
        return set()



class PersistantObserver(Observer):
    def __init__(self, *args, **kwargs):
        """
        Check if watching folders has changed since last observation.
        If change detected, emit corresponding events at suscribers handlers.
        At the `Observer.stop`, save states of folders with pickle for the next observation.

        PARAMETERS
        ==========
        save_to : unicode
            path where save pickle dumping
        protocol (optionnal): int
            protocol used for dump current states of watching folders
        """
        self._filename = kwargs.pop('save_to')
        self._protocol = kwargs.pop('protocol', 0)
        Observer.__init__(self, *args, **kwargs)


    def start(self, *args, **kwargs):
        previous_snapshots = dict()
        if os.path.exists(self._filename):
            with open(self._filename) as f:
                previous_snapshots = pickle.load(f)

        for watcher, handlers in self._handlers.iteritems():
            path = watcher.path
            curr_snap = DirectorySnapshot(path)
            pre_snap = previous_snapshots.get(path, _EmptySnapshot())
            diff = DirectorySnapshotDiff(pre_snap, curr_snap)
            for handler in handlers:
                # Dispatch files modifications
                for new_path in diff.files_created:
                    handler.dispatch(FileCreatedEvent(new_path))
                for del_path in diff.files_deleted:
                    handler.dispatch(FileDeletedEvent(del_path))
                for mod_path in diff.files_modified:
                    handler.dispatch(FileModifiedEvent(mod_path))
                for mov_path in diff.files_moved:
                    handler.dispatch(FileMovedEvent(mov_path))

                # Dispatch directories modifications
                for new_dir in diff.dirs_created:
                    handler.dispatch(DirCreatedEvent(new_dir))
                for del_dir in diff.dirs_deleted:
                    handler.dispatch(DirDeletedEvent(del_dir))
                for mod_dir in diff.dirs_modified:
                    handler.dispatch(DirModifiedEvent(mod_dir))
                for mov_dir in diff.dirs_moved:
                    handler.dispatch(DirMovedEvent(mov_dir))

        Observer.start(self, *args, **kwargs)


    def stop(self, *args, **kwargs):
        snapshots = {handler.path : DirectorySnapshot(handler.path) for handler in self._handlers.iterkeys()}
        with open(self._filename, 'wb') as f:
            pickle.dump(snapshots, f, self._protocol)
        Observer.stop(self, *args, **kwargs)


if __name__ == "__main__":
    # Simple exemple, derivated from watchdog doc.
    import logging
    from watchdog.events import LoggingEventHandler
    logging.basicConfig(level=logging.DEBUG)
    event_handler = LoggingEventHandler()
    observer = PersistantObserver(save_to='/tmp/test.pickle', protocol=-1)
    observer.schedule(event_handler, path='/tmp/test', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
