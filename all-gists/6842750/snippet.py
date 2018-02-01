#! /usr/bin/python2.7
# coding: utf-8


import threading


class WatchDog(object):
    def __init__(self, interval, callback):
        self.interval = interval # second
        self.callback = callback
        self.timer = None

    def _callback(self):
        self.deactivate()
        self.callback()
        self.activate()

    def keepalive(self):
        self.deactivate()
        self.activate()

    def activate(self):
        self.timer = threading.Timer(self.interval, self._callback)
        self.timer.start()

    def deactivate(self):
        self.timer.cancel()

    def __call__(self):
        self._callback()



def main():
    from time import gmtime, strftime
    def callback():
        print 'call',strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    wd = WatchDog(3, callback)
    wd.activate()

    while True:
        a = raw_input()
        wd.keepalive()

    wd.deactivate()



main()
