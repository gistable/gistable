#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
from time import strftime

clocks = {'12:00': '🕛', '12:30': '🕧',  '1:00': '🕐',  '1:30': '🕜',
           '2:00': '🕑',  '2:30': '🕝',  '3:00': '🕒',  '3:30': '🕞',
           '4:00': '🕓',  '4:30': '🕟',  '5:00': '🕔',  '5:30': '🕠',
           '6:00': '🕕',  '6:30': '🕡',  '7:00': '🕖',  '7:30': '🕢',
           '8:00': '🕗',  '8:30': '🕣',  '9:00': '🕘',  '9:30': '🕤',
          '10:00': '🕙', '10:30': '🕥', '11:00': '🕚', '11:30': '🕦'} 

# Get the argument, which should be a time string, like "8:10."
# If there's no argument, use the current time.
try:
  oclock = argv[1]
except IndexError:
  oclock = strftime('%I:%M')

hour, minute = [ int(x) for x in oclock.split(':') ]

# Round to the nearest half-hour, because there are no
# emoji clockfaces for other times.
rminute = int(round(float(minute)/30)*30)
if rminute == 60:
  rminute = 0
  hour = 1 if hour == 12 else hour + 1

print clocks['%d:%02d' % (hour, rminute)]
