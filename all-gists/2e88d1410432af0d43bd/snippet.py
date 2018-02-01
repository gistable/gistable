#!/usr/bin/env python

import sys
from os import environ

if 'DISPLAY' not in environ:
    exit(0)

name = "rhythmbox"
if len(sys.argv) > 1:
    name = sys.argv[1]

import dbus

bus = dbus.SessionBus()

try:
    proxy = bus.get_object("org.mpris.MediaPlayer2.%s" % name, "/org/mpris/MediaPlayer2")
    device_prop = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")

    prop = device_prop.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    status = device_prop.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
except dbus.exceptions.DBusException:
    # Probably not running.
    exit(0)

if status == "Playing":
    print (prop.get("xesam:artist")[0] + " - " + prop.get("xesam:title")).encode('utf-8')
else:
    print "Not playing."
