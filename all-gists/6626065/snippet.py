#!/usr/bin/python

"""
Control volume on an alsamixer in ubuntu from the command line using python-alsaaudio

Written for Crouton Chromebooks to have easy hotkeys for their volume control in ubuntu.

https://github.com/dnschneid/crouton/wiki/Keyboard

usage:
    volume up
    volume down
    volume mute
"""

try:
    import alsaaudio
except ImportError:
    print("No python-alsaaudio, please type: sudo apt-get install python-alsaaudio")

import sys

def volume(new_v):
    if new_v > 100:
        new_v = 100
    if new_v < 0:
        new_v = 0
    m.setvolume(new_v)

m = alsaaudio.Mixer()
v = m.getvolume()[0]
command = sys.argv[1].strip().lower()

if command == 'up':
    volume(v + 10)
elif command == 'down':
    volume(v - 10)
elif command == 'mute':
    new_mute = not m.getmute()[0]
    m.setmute(new_mute)


