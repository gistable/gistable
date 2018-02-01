#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import select
from select import kqueue, kevent


class Watch(object):
    SIZE_HINT = 50000

    def __init__(self, appdir, callback):
        self.kqueue = kqueue()
        self.kcontrol = self.kqueue.control
        self.fds = {}
        self.paths = {}
        self.appdir = appdir
        self.callback = callback
        self.register_path(appdir)

    def register(self, fd, path):
        assert fd not in self.fds
        self.fds[fd] = path
        self.paths[path] = fd
        ev = [select.kevent(
            fd,
            filter=select.KQ_FILTER_VNODE,
            flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_CLEAR,
            fflags=select.KQ_NOTE_DELETE | select.KQ_NOTE_EXTEND |
            select.KQ_NOTE_WRITE | select.KQ_NOTE_ATTRIB
            )]
        self.kcontrol(ev, 0, 0)


    def unregister(self, fd):
        if fd in self.fds:
            ev = [select.kevent(
                fd,
                filter=select.KQ_FILTER_VNODE, flags=select.KQ_EV_DELETE,
                fflags=select.KQ_NOTE_DELETE | select.KQ_NOTE_EXTEND |
                select.KQ_NOTE_WRITE | select.KQ_NOTE_ATTRIB
                )]
            self.kcontrol(ev,  0, 0)
            del self.paths[self.fds[fd]]
            del self.fds[fd]

    def register_path(self, path):
        for root, dirs, files in os.walk(path):
            print "-", root, dirs, files
            if root not in self.paths:
                print "register %s" % root
                fd = os.open(root, os.O_RDONLY)
                self.register(fd, root)
                for f in files:
                    fp = os.path.join(root, f)
                    print fp
                    fd = os.open(fp, os.O_RDONLY)
                    self.register(fd, fp)
                    

    def loop(self):
        try:
            while True:
                events = self.kcontrol([], self.SIZE_HINT, None)
                for ev in events:
                    fd = ev.ident
                    path = self.fds[fd]
                    if ev.fflags & select.KQ_NOTE_DELETE:
                        self.unregister(fd)
                    elif ev.fflags & select.KQ_NOTE_EXTEND or ev.fflags & select.KQ_NOTE_WRITE:
                        self.register_path(self.fds[fd])
                    print "event:", path, ev
                    self.callback(path)
        except KeyboardInterrupt:
            self.kqueue.close()
            for fd in self.events:
                os.close(fd)

if __name__ == "__main__":
    def test(path):
        print path

    watch = Watch("/Users/bd/tmp/app", test)
    watch.loop()
