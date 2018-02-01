#!/usr/bin/env python
# Author: Chris Eberle <eberle1080@gmail.com>
# Watch for any changes in a module or package, and reload it automatically

import pyinotify
import imp
import os

class ModuleWatcher(pyinotify.ProcessEvent):
    """
    Automatically reload any modules or packages as they change
    """

    def __init__(self):
        "El constructor"

        self.wm = pyinotify.WatchManager()
        self.notifier = None
        self.mod_map = {}

    def _watch_file(self, file_name, module):
        "Add a watch for a specific file, and map said file to a module name"

        file_name = os.path.realpath(file_name)
        self.mod_map[file_name] = module
        self.wm.add_watch(file_name, pyinotify.EventsCodes.IN_MODIFY)
        #print 'Watching', file_name

    def watch_module(self, name):
        "Load a module, determine which files it uses, and watch them"

        if imp.is_builtin(name) != 0:
            # Pretty pointless to watch built-in modules
            return

        (fd, pathname, description) = imp.find_module(name)

        try:
            mod = imp.load_module(name, fd, pathname, description)
            if fd:
                self._watch_file(fd.name, name)
            else:
                for root, dirs, files in os.walk(pathname):
                    for filename in files:
                        fpath = os.path.join(root, filename)
                        if fpath.endswith('.py'):
                            self._watch_file(fpath, name)
        finally:
            if fd:
                fd.close()

    def start_watching(self):
        "Start the pyinotify watch thread"

        if self.notifier is None:
            self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
        self.notifier.start()

    def stop_watching(self):
        "Stop the pyinotify watch thread"

        if self.notifier is not None:
            self.notifier.stop()

    def process_IN_MODIFY(self, event):
        "A file of interest has changed"

        # Is it a file I know about?
        if event.path not in self.mod_map:
            return

        # Find out which module is using that file
        modname = self.mod_map[event.path]

        # Reload the module
        (fd, pathname, description) = imp.find_module(modname)
        try:
            imp.load_module(modname, fd, pathname, description)
        finally:
            if fd:
                fd.close()

        #print 'Reload', modname

if __name__ == '__main__':
    # Test everything

    import sys

    mw = ModuleWatcher()
    mw.watch_module('module1')
    mw.watch_module('module2')
    mw.start_watching()

    try:
        raw_input('Press ENTER to exit')
    finally:
        mw.stop_watching()
        sys.exit(0)
