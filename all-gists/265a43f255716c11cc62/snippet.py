#!/usr/bin/python

import dbus
import dbus.glib
import gobject
import subprocess


def lock():
    print "Screen saver turned on"
    subprocess.call("pactl set-sink-mute 0 1", shell=True)
    subprocess.call("xchat -e -c 'AWAY'", shell=True)


def unlock():
    subprocess.call("pactl set-sink-mute 0 0", shell=True)
    subprocess.call("xchat -e -c 'BACK'", shell=True)
    print "Screen saver deactivated"


def main(args):
    bus = dbus.SessionBus()

    # listen for changes in screensaver activity
    bus.add_signal_receiver(
        lock,
        'Locked',
        dbus_interface='com.canonical.Unity.Session')

    bus.add_signal_receiver(
        unlock,
        'Unlocked',
        dbus_interface='com.canonical.Unity.Session')

    mainLoop = gobject.MainLoop()
    mainLoop.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
