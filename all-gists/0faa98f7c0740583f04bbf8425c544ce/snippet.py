# Disable password protection on an Alto disk by zeroing out the password flag in sys.boot

import sys
import subprocess

diskContents = None

# Get word at the word offset in the disk file
def getWord(wordOffset):
  return ord(diskContents[2 * wordOffset]) + ord(diskContents[2 * wordOffset + 1]) * 256

def getSector(addr):
  # Convert address (sector/cylinder/head) into a linear address
  sec = addr >> 12
  cyl = (addr >> 3) & 0x1ff
  h = 1 if (addr & 0x4) else 0

  n = sec + (cyl*2 + h) * 12
  offset = n*(256 + 10 + 1)
  header = [getWord(offset + i) for i in range(1, 3)]
  label = [getWord(offset + i) for i in range(3, 11)]
  data = [getWord(offset + i) for i in range(11, 267)]
  return header, label, data, offset
  
# Print the specified sector label
def printLabel(label):
  print 'next: %04x, previous: %04x, numChars: %d, pageNumber: %x, fileId: (v %x, %x %x)' % (label[0], label[1], label[3], label[4], label[5], label[6], label[7])

def main():
  global diskContents

  # Read disk contents
  filename = 'parc-37-wyatt-mesa-3.dsk'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  with open(filename) as f:
    diskContents = f.read()

  # Read sector 0 of disk, i.e. copy of sys.boot
  header, label, data, offset = getSector(0)
  printLabel(label)

  # Read second sector of sys.boot, using the next block pointer in the label
  nextAddr = label[0]
  header, label, data, offset = getSector(nextAddr)
  printLabel(label)

  print 'Password vector:',
  for word in data[128:128+9]:
    print '%04x' % word,
  print

  # Zero the password flag word
  with open(filename, 'r+') as f:
    # Seek to word 128 in sector, skipping 11 words of header + label
    f.seek((offset + 11 + 128) * 2)
    f.write('\0\0')

if __name__ == "__main__":
  main()
