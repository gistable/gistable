#!/usr/bin/env python
import sys

keyPIN = str(int(sys.argv[1]))

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
G1 Z-0.06 ( plunge! )
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

granularity = 20

for cutPass in range(1, granularity+1):
  print ""
  if cutPass % 2 == 0:
    reverse = True
    print "( start pass %s in reverse )"%(cutPass)
  else:
    reverse = False
    print "( start pass %s in forward )"%(cutPass)
  if reverse:
    pinSet = reversed(range(0, len(keyPIN)))
  else:
    pinSet = range(0, len(keyPIN))
  for pinNumber in pinSet:
    pinType = int(keyPIN[pinNumber])
    pinCenter = pinPositions[pinNumber]
    pinDepth = pinDepths[pinType] * (cutPass / float(granularity))

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

print ""
print "M2"