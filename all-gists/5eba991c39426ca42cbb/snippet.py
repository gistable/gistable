#!/usr/bin/env python
#
# Replacement `MtimeFileWatcher` for App Engine SDK's dev_appserver.py,
# designed for OS X. Improves upon existing file watcher (under OS X) in
# numerous ways:
#
#   - Uses FSEvents API to watch for changes instead of polling. This saves a
#     dramatic amount of CPU, especially in projects with several modules.
#   - Tries to be smarter about which modules reload when files change, only
#     modified module should reload.
#
# Install:
#   $ pip install macfsevents
#   $ cp mtime_file_watcher.py \
#        sdk/google/appengine/tools/devappserver2/mtime_file_watcher.py
import os
import time
from fsevents import Observer
from fsevents import Stream
from os.path import abspath, join

GOPATH = os.environ['GOPATH'].split(':')[0]
PROJECT_DIR = abspath(join(GOPATH, '..', '..'))

# Set of packages I want to watch for changes in that are shared among modules.
# That is, when any of these change, ALL of the modules should be restarted.
NON_MODULE_DIRS = [join(PROJECT_DIR, p) for p in os.listdir(PROJECT_DIR) if
                   p not in set(['api', 'checkout', 'platform', 'preorder', 'store']) and
                   not p.startswith('.') and
                   p != "assets" and
                   p != "node_modules" and
                   p != "resources" and
                   p != "static" and
                   p != "test"]

# Only watch for changes to .go or .yaml files
WATCHED_EXTENSIONS = set(['.go', '.yaml'])


class MtimeFileWatcher(object):
    SUPPORTS_MULTIPLE_DIRECTORIES = True

    def __init__(self, directories, **kwargs):
        self._changes = _changes = []

        # Path to current module
        module_dir = directories[0]

        # Paths to watch
        paths = [module_dir]

        # Explicitly adding paths outside of module dir.
        for path in NON_MODULE_DIRS:
            paths.append(path)

        self.observer = Observer()

        def callback(event, mask=None):
            # Get extension
            try:
                ext = os.path.splitext(event.name)[1]
            except IndexError:
                ext = None

            # Add to changes if we're watching a file with this extension.
            if ext in WATCHED_EXTENSIONS:
                _changes.append(event.name)

        self.stream = Stream(callback, file_events=True, *paths)

    def start(self):
        self.observer.schedule(self.stream)
        self.observer.start()

    def changes(self, timeout=None):
        time.sleep(0.1)
        changed = set(self._changes)
        del self._changes[:]
        return changed

    def quit(self):
        self.observer.unschedule(self.stream)
        self.observer.stop()
        self.observer.join()