#!/usr/bin/env python
# encoding: utf-8

import sys
import os

# We need to import the relvant object definitions from PyObjC
from AppKit import *
from PyObjCTools import AppHelper

# Cocoa prefers composition to inheritance. The members of an object's
# delegate will be called upon the happening of certain events. Once we define
# methods with particular names, they will be called automatically
class Delegate (NSObject):
    def applicationDidFinishLaunching_(self, aNotification):
        '''Called automatically when the application has launched'''
        print "Hello, World!"

    def windowWillClose_(self, aNotification):
        '''Called automatically when the window is closed'''
        print "Window has been closed"
        # Terminate the application
        NSApp().terminate_(self)


def main():
    # Create a new application instance ...
    a=NSApplication.sharedApplication()
    # ... and create its delgate.  Note the use of the
    # Objective C constructors below, because Delegate
    # is a subcalss of an Objective C class, NSObject
    delegate = Delegate.alloc().init()
    # Tell the application which delegate object to use.
    a.setDelegate_(delegate)

    # Now we can can start to create the window ...
    frame = ((200.0, 300.0), (250.0, 100.0))
    # (Don't worry about these parameters for the moment. They just specify
    # the type of window, its size and position etc)
    w = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(frame, 15, 2, 0)
    # ... tell it which delegate object to use (here it happens
    # to be the same delegate as the application is using)...
    w.setDelegate_(delegate)
    # ... and set some properties. Unicode strings are preferred.
    w.setTitle_(u'Hello, World!')
    # All set.  Now we can show the window ...
    w.orderFrontRegardless()
    # ... and start the application
    AppHelper.runEventLoop()

if __name__ == '__main__':
    main()
