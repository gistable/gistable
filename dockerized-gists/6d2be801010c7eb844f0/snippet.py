#!/usr/bin/python
import serial
import sys

latestByte  = ('c')
lastByte    = ('c')
inPacket    = False
myPacket    = []
PLENGTH     = 0

EEGVALUES    = []
EEGRAWVALUES = []

def parsePacket():
  if checksum():
    i=1
    while i < len(myPacket) - 1:
      if ord(myPacket[i]) == 0x02:
        POOR_SIGNAL = ord(myPacket[i+1])
        i += 2
      elif ord(myPacket[i]) == 0x04:
        ATTENTION = ord(myPacket[i+1])
        i += 2
      elif ord(myPacket[i]) == 0x05:
        MEDITATION = ord(myPacket[i+1])
        i += 2
      elif ord(myPacket[i]) == 0x16:
        BLINK_STRENGTH = ord(myPacket[i+1])
        i += 2
      elif ord(myPacket[i]) == 0x83:
        for c in xrange(i+1, i+25, 3):
          EEGVALUES.append(ord(myPacket[c]) << 16 | ord(myPacket[c+1]) << 8 | ord(myPacket[c+2]))
        i += 26
      elif ord(myPacket[i]) == 0x80:
        EEGRAWVALUES = ord(myPacket[i+1]) << 8 | ord(myPacket[i+2])
        i += 4
    print "%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (POOR_SIGNAL,ATTENTION,MEDITATION,EEGVALUES[0],EEGVALUES[1],EEGVALUES[2],EEGVALUES[3],EEGVALUES[4],EEGVALUES[5],EEGVALUES[6],EEGVALUES[7])
  else:
    print "Invalid Checksum!"

def checksum():
  x = 0
  for i in range(1, len(myPacket) -1):
    x += ord(myPacket[i])
  return ~(x&255) & 0b11111111 == ord(myPacket[len(myPacket)-1])

def readCSV():
  global myPacket, lastByte, LatestByte, inPacket, PLENGTH
  ser = serial.Serial(
      port=sys.argv[1],
      baudrate=9600,
      parity=serial.PARITY_NONE,
      stopbits=serial.STOPBITS_ONE,
      bytesize=serial.SEVENBITS
  )

  ser.isOpen()
  try:
    while 1 :
      while ser.inWaiting() > 0:
        latestByte = ser.read(1)

        if ord(lastByte) == 170 and ord(latestByte) == 170 and inPacket == False:
          inPacket   = True

        elif len(myPacket) == 1:
          myPacket.append(latestByte)
          PLENGTH = ord(myPacket[0])

        elif inPacket == True:
          myPacket.append(latestByte)
          if len(myPacket) > 169:
            print "Error: Data Error too long!"
            del myPacket[:]
            inPacket = False
            del EEGVALUES[:]
          elif len(myPacket) == PLENGTH + 2:
            parsePacket()
            del myPacket[:]
            inPacket = False
            del EEGVALUES[:]


        lastByte = latestByte

  except KeyboardInterrupt:
    print('Exiting...')
    if ser.isOpen():
      ser.close();
    sys.exit(0)

if len(sys.argv) < 2:
  print "Mindflex datalogger by David gouveia <david.gouveia@gmail.com>"
  print "Usage: %s <COM PORT>" % sys.argv[0]
  sys.exit(1)

readCSV()