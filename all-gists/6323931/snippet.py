#!/usr/bin/env python
import dbus
import collections
import sys
import os

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Usage: mumble-broadcast <message>"
    sys.exit(1)

  user = os.environ.get("USER", "system")
  message = u"Message from {0}: {1}".format(user, sys.argv[1])

  Player = collections.namedtuple("Player", "session mute deaf suppressed selfMute selfDeaf channel id name onlinesecs bytespersecond")
  Channel = collections.namedtuple("Channel", "id name parent links")

  dbus_base = 'net.sourceforge.mumble.murmur'
  bus = dbus.SystemBus()
  proxy = bus.get_object(dbus_base, '/1')
  murmur = dbus.Interface(proxy, 'net.sourceforge.mumble.Murmur')

  for p in murmur.getPlayers():
    player = Player(*p)
    murmur.sendMessage(player.session, message)

  sys.exit(0)
