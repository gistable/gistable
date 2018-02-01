"""mk2mpris.py: forward GNOME media key events to an MPRIS2 player.
"""
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

APP_NAME = 'mk2mpris'
DBUS_INTERFACE_MK = 'org.gnome.SettingsDaemon.MediaKeys'
OBJ_PATH_MK = '/org/gnome/SettingsDaemon/MediaKeys'
OBJ_NAME_GSETTINGS = 'org.gnome.SettingsDaemon'
OBJ_MPRIS2_BASE = 'org.mpris.MediaPlayer2'
OBJ_PATH_MPRIS2 = '/org/mpris/MediaPlayer2'

def forward_keys(player):
    """Forward Gnome media keys to the named MPRIS2 player."""
    player_obj = '{0}.{1}'.format(OBJ_MPRIS2_BASE, player)

    def handle_key(app_name, key):
        print key
        if key == 'Play':
            # Send the PlayPause message on MPRIS.
            player = bus.get_object(player_obj, OBJ_PATH_MPRIS2)
            player.PlayPause()

    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    loop = gobject.MainLoop()

    media_keys = bus.get_object(
        OBJ_NAME_GSETTINGS,
        OBJ_PATH_MK,
    )
    media_keys.GrabMediaPlayerKeys(
        APP_NAME,
        0,
        dbus_interface=DBUS_INTERFACE_MK
    )

    bus.add_signal_receiver(
        handle_key,
        None,  # Match all signal names.
        DBUS_INTERFACE_MK,
        None,  # Match all senders.
        OBJ_PATH_MK,
    )

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        media_keys.ReleaseMediaPlayerKeys(
            APP_NAME,
            dbus_interface=DBUS_INTERFACE_MK,
        )

if __name__ == '__main__':
    forward_keys('tomahawk')
