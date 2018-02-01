#!/usr/bin/env python

""" 
Spotify Screensaver Toggle
By Stuart Colville
http://muffinresearch.co.uk/

Requires Spotify Linux Preview.

"""

import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop

class SpotifyScreenSaverPause(object):
    """This pauses and plays spotify when the screensaver is activated"""

    def __init__(self):
        """init class."""
        dbus_loop = DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus(mainloop = dbus_loop)
        self.loop = gobject.MainLoop()
        self.start_listen()
        self.was_playing = 0
        self.loop.run()

    def start_listen(self):
        """Listen to screensaver ActiveChanged events from dbus."""
        screensaver = self.bus.get_object('org.gnome.ScreenSaver', 
                                          '/org/gnome/ScreenSaver')
        screensaver.connect_to_signal("ActiveChanged", self.play_pause)

    def play_pause(self, *args, **kwargs):
        """Toggle play/pause."""
        try:
            spotify = self.bus.get_object('org.mpris.MediaPlayer2.spotify', 
                                          '/org/mpris/MediaPlayer2')
            spotify_iface = dbus.Interface(spotify, 
                dbus_interface='org.mpris.MediaPlayer2.Player')
            props_iface = dbus.Interface(spotify, 
                dbus_interface='org.freedesktop.DBus.Properties')
            if self.was_playing:
                spotify_iface.PlayPause()
                self.was_playing = 0
            else:
                if props_iface.Get('org.mpris.MediaPlayer2.Player', 
                                   'PlaybackStatus') == 'Playing':
                    self.was_playing = 1
                spotify_iface.Pause()
        # Ignore exception caused by spotify not being started.
        except dbus.exceptions.DBusException, e:
            if e.get_dbus_name() != 'org.freedesktop.DBus.Error.ServiceUnknown':
                raise

if __name__ == "__main__":
    ss = SpotifyScreenSaverPause()