#!/usr/bin/python3

from evdev import InputDevice
from syslog import syslog

switch = InputDevice('/dev/input/by-path/platform-thinkpad_acpi-event')
trackpoint = InputDevice('/dev/input/event4')
touchpad = InputDevice('/dev/input/event5')

print(switch)
print(trackpoint)
print(touchpad)

for ev in switch.read_loop():
    if ev.type == 5:
        if ev.value == 1:
            print('tablet!')
            syslog('converting to tablet')
            trackpoint.grab()
            touchpad.grab()
        if ev.value == 0:
            print('laptop!')
            syslog('converting to laptop')
            trackpoint.ungrab()
            touchpad.ungrab()
