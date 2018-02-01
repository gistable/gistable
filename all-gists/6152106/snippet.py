#!/usr/bin/python

import sys, dbus
knotify = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
try:    title, text = sys.argv[1:3]
except: print 'Usage: knotify.py title text'; sys.exit(1)
knotify.event("warning", "kde", [], title, text, [], [], 0, 0, dbus_interface="org.kde.KNotify")
