import struct
import sys

def getBytes(fs, pos, numBytes):
  fs.seek(pos)
  byte = fs.read(numBytes)
  if (numBytes == 2):
    formatString = "H"
  elif (numBytes == 1):
    formatString = "B"
  elif (numBytes == 4):
    formatString = "i"
  else:
    raise Exception("Not implemented")
  return struct.unpack("<"+formatString, byte)[0]

def getString(fs, pos, numBytes):
  fs.seek(pos)
  raw = fs.read(numBytes)
  return struct.unpack(str(numBytes)+"s", raw)[0]

def bytesPerSector(fs):
  return getBytes(fs,11,2)

def sectorsPerCluster(fs):
  return getBytes(fs,13,1)

def reservedSectorCount(fs):
  return getBytes(fs,14,2)

def numberOfFATs(fs):
  return getBytes(fs,16,1)

def FATStart(fs, numFat):
  return reservedSectorCount(fs) * bytesPerSector(fs)

def FATSize(fs):
  return getBytes(fs, 36, 4)

def rootStart(fs):
  return FATStart(fs,1) + (FATSize(fs) * numberOfFATs(fs) * bytesPerSector(fs))

def fsIdentityString(fs):
  return getString(fs,82,8)

def getDirTableEntry(fs):
  offset = rootStart(fs)
  while True:
    fs.seek(offset + 0x0B)
    isLFN = (struct.unpack("b", fs.read(1))[0] == 0x0F)
    if isLFN:
      fileName = "SKIPPED"
    else:
      fs.seek(offset)
      fileName = struct.unpack("8s", fs.read(8))[0]
    offset += 32
    yield (isLFN, fileName)

def ppNum(num):
  return "%s (%s)" % (hex(num), num)

fs = open(sys.argv[1],"rb")
print "Bytes per sector:",        ppNum(bytesPerSector(fs))
print "Sectors per cluster:",     ppNum(sectorsPerCluster(fs))
print "Reserved sector count:",   ppNum(reservedSectorCount(fs))
print "Number of FATs:",          ppNum(numberOfFATs(fs))
print "Start of FAT1:",           ppNum(FATStart(fs, 1))
print "Start of root directory:", ppNum(rootStart(fs))
print "Identity string:",         fsIdentityString(fs)
print "Files & directories:"
for fn in getDirTableEntry(fs):
  print fn[1]
  raw_input()
