#!/usr/bin/env python
  
import random
import struct
import sys

# Most of the Fat32 class was cribbed from https://gist.github.com/jonte/4577833
  
def ppNum(num):
  return "%s (%s)" % (hex(num), num)
  
class Fat32:
    def __init__(self, filename):
        self.fs = open(filename, 'r+b')
  
    def getRawBytes(self, pos, numBytes):
        self.fs.seek(pos)
        return self.fs.read(numBytes)
  
    def putRawBytes(self, pos, data):
        self.fs.seek(pos)
        self.fs.write(data)
  
    def putUInt32(self, pos, n):
        print 'write %10s@%08x' % (n, pos) 
        self.fs.seek(pos)
        self.putRawBytes(pos, struct.pack('<i', n))
  
    def putUInt16(self, pos, n):
        self.fs.seek(pos)
        self.putRawBytes(pos, struct.pack('<H', n))
  
    def putUInt8(self, pos, n):
        self.fs.seek(pos)
        self.putRawBytes(pos, struct.pack('<B', n))
  
    def getBytes(self, pos, numBytes):
        byte = self.getRawBytes(pos, numBytes)
        if (numBytes == 2):
            formatString = "H"
        elif (numBytes == 1):
            formatString = "B"
        elif (numBytes == 4):
            formatString = "i"
        else:
            raise Exception("Not implemented")
        return struct.unpack("<"+formatString, byte)[0]
  
    def getString(self, pos, numBytes):
        raw = self.getRawBytes(pos, numBytes)
        return struct.unpack(str(numBytes)+"s", raw)[0]
  
    @property
    def bytesPerSector(self):
        return self.getBytes(11,2)
  
    @property
    def sectorsPerCluster(self):
        return self.getBytes(13,1)
  
    @property
    def bytesPerCluster(self):
        return self.bytesPerSector * self.sectorsPerCluster
  
    @property
    def reservedSectorCount(self):
        return self.getBytes(14,2)
  
    @property
    def numberOfFATs(self):
        return self.getBytes(16,1)
  
    def FATStart(self, numFat):
        return self.reservedSectorCount * self.bytesPerSector + (self.FATSize * self.bytesPerSector * (numFat - 1))
  
    def FATEnd(self, numFat):
        return self.FATStart(numFat+1)
  
    @property
    def FATSize(self):
        return self.getBytes(36,4)
  
    @property
    def rootStart(self):
        return self.FATStart(1) + (self.FATSize * self.numberOfFATs * self.bytesPerSector)
  
    @property
    def fsIdentityString(self):
        return self.getString(82,8)
  
class ClEntry:
    def __init__(self, offset, length, nextclidx, prevclidx=None):
        self.offset = offset
        self.length = length
        self.next = nextclidx
        self.prev = prevclidx
  
    def __repr__(self):
        return 'ClEnt(%s, %s, %s, %s)' % (self.offset, self.length, self.next, self.prev)
  
class Clusters:
    def __init__(self, fs):
        self.fs = fs
        self.fat = []
        self.free = set()
        self.fs.fs.seek(0, 2)
        eof = self.fs.fs.tell()
        for pos in range(self.fs.FATStart(1), self.fs.FATEnd(1), 4):
            clidx = (pos - self.fs.FATStart(1)) / 4
            # not entirely sure why -2 is required here
            offset = self.fs.rootStart + (clidx-2) * self.fs.bytesPerCluster
            if offset + self.fs.bytesPerCluster >= eof:
                break
            nextcluster = self.fs.getBytes(pos, 4)
            self.fat.append(ClEntry(offset, self.fs.bytesPerCluster, nextcluster))
            if nextcluster == 0:
                self.free.add(clidx)
  
        for clidx in xrange(0, len(self.fat)):
            cluster = self.fat[clidx]
            if cluster.next > 2 and cluster.next < 0xffffff8:
                self.fat[cluster.next].prev = clidx
  
    def setNextCluster(self, target, value):
        if value is None:
            value = 0
        if target is not None:
            writeOffset = self.fs.FATStart(1) + target * 4
            self.fs.putUInt32(writeOffset, value)
            self.fat[target].next = value
            if value == 0:
                # clear the previous cluster reference
                self.fat[target].prev = None
                # add cluster to the free list
                self.free.add(target)
            else:
                if value < 0xffffff8:
                    # set the previous cluster reference 
                    self.fat[value].prev = target
                # remove cluster from the free list
                self.free.discard(target)
  
    def swap(self, clidx1, clidx2):
        c1 = self.fat[clidx1]
        c2 = self.fat[clidx2]
  
        n1 = c1.next
        n2 = c2.next
  
        p1 = c1.prev
        p2 = c2.prev
  
        o1 = c1.offset
        o2 = c2.offset
  
        d1 = self.fs.getRawBytes(o1, c1.length)
        d2 = self.fs.getRawBytes(o2, c2.length)
  
        self.setNextCluster(p1, clidx2)
        self.setNextCluster(clidx2, n1)
        self.setNextCluster(p2, clidx1)
        self.setNextCluster(clidx1, n2)
  
        print o1
        print o2
        self.fs.putRawBytes(o1, d2)
        self.fs.putRawBytes(o2, d1)
  
fs = Fat32(sys.argv[1])
print "Bytes per sector:",        ppNum(fs.bytesPerSector)
print "Sectors per cluster:",     ppNum(fs.sectorsPerCluster)
print "Reserved sector count:",   ppNum(fs.reservedSectorCount)
print "Size of FAT (sectors):",   ppNum(fs.FATSize)
print "Number of FATs:",          ppNum(fs.numberOfFATs)
print "Start of FAT1:",           ppNum(fs.FATStart(1))
print "Start of root directory:", ppNum(fs.rootStart)
print "Identity string:",         fs.fsIdentityString
clusters = Clusters(fs)
if 0:
    clusters.swap(4, 6)
    clusters.fs.fs.flush()
    sys.exit(0)
for arg in sys.argv[2:]:
    clidx = clusters.fat[int(arg)].next
    while clidx > 2 and clidx < 0xffffff8:
        free = random.sample(clusters.free, 1)[0]
        nextidx = clusters.fat[clidx].next
        print 'swap %10s <=> %10s next %10s' % (clidx, free, nextidx)
        clusters.swap(clidx, free)
        clidx = nextidx
#print clusters.fat
#clusters.swap(5, 9)
#clusters.swap(6, 10)
clusters.fs.fs.flush()