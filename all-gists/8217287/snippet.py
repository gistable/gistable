#!/usr/bin/env python
# makekey.py - A key making tool
# This program will accept a pin configuration for a Schalge 5 Pin lock and produce GCode to mill out the corresponding key.
#
# For example, this will produce a bump key:
# $ ./makekey.py 99999
#
# This could produce a key to something else:
# $ ./makekey.py 38457
#
# My dearest apologies if that happens to be yours.
#
# This is also a real key, as there does not exist a 'missing' pin:
# $ ./makekey.py 00000
#
# Author: Torrie "tdfischer" Fischer <tdfischer@hackerbots.net>
#
# Made at Noisebridge 1/1/14 on visit from SYNHAK <3
# https://noisebridge.net/wiki/Key_Milling
#

import sys

# CONFIGURATION OPTIONS

# granularity: How many passes you want to mill with
granularity = 10

# invert: True if you're cutting the key upside down
invert = False

# key_thickness: How thick the key is in total
# useful if you're stuck without a straight edge bit
key_thickness = 0.06

keyPIN = str(sys.argv[1])

print """
G94 ( use inches/min feed rate)
G20 ( use inches for coordinates )
G90 ( absolute coordinates )
G64 P0.00500 ( maximum deviation )
S10484 ( spindle speed for brass )
G0 Z0.1 ( lift up to avoid hitting the key )
G0 X0 Y0 ( move to the blade, just at the edge of the shoulder )
M3 ( start cutting )
G1 F3000 X-0.1 ( move over to the side before cutting the side off )
G1 X0 Y0 ( move into the key blade)
G1 Y0.05 ( move down the shoulder )"""

pinPositions = [
  0.231,
  0.387,
  0.543,
  0.699,
  0.855
]

pinDepths = [
  0.005,
  0.020,
  0.035,
  0.050,
  0.065,
  0.080,
  0.095,
  0.110,
  0.125,
  0.140
]

for cutLayer in range(1, granularity+1):
  layerDepth = key_thickness * (cutLayer / float(granularity))
  print "G1 Z-%s ( start layer %s )"%(layerDepth, cutLayer)
  for cutPass in range(1, granularity+1):
    print ""
    if cutPass % 2 == 0:
      reverse = True
      print "( start pass %s in reverse, layer %s )"%(cutPass, cutLayer)
    else:
      reverse = False
      print "( start pass %s in forward, layer %s )"%(cutPass, cutLayer)
    if reverse:
      pinSet = reversed(range(0, len(keyPIN)))
    else:
      pinSet = range(0, len(keyPIN))
    for pinNumber in pinSet:
      pinType = int(keyPIN[pinNumber])
      pinCenter = pinPositions[pinNumber]
      pinDepth = pinDepths[pinType] * (cutPass / float(granularity))

      if invert:
        pinDepth = -pinDepth

      pinStart = pinCenter - 0.035
      pinEnd = pinCenter + 0.035

      if reverse:
        print "G1 Y%s X%s ( cut pin type %s at %s )"%(pinEnd, pinDepth, pinType, pinNumber)
        print "G1 Y%s"%(pinStart)
      else:
        print "G1 Y%s X%s ( cut pin type %s at %s )"%(pinStart, pinDepth, pinType, pinNumber)
        print "G1 Y%s"%(pinEnd)
    if reverse:
      print "G1 X0 Y0.05 ( move back down to the shoulder )"
    else:
      print "G1 Y1.17"

print ""
print "M2"