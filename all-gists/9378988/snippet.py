#!/usr/bin/python

import sys

DEBUG = False
HEADER_ONLY = False

if len(sys.argv) >= 2:
  FILENAME = sys.argv[1]
  if len(sys.argv) >= 3:
    DEBUG = True
    if len(sys.argv) == 4:
      HEADER_ONLY = True
else:  
  print "USAGE: rdump.py FILENAME [debug]"
  sys.exit(1)


"""
offsets in strings header: 
0 - 1: type ID
2 - 4: header size
4 - 7: total block size (size of file)
8 - b: string count
c - f: style count # dont care about styles
14 - 17: strings start
18 - 1b: styles start # dont care about styles
"""

def trim_bytes(l, number):
  x = []
  i = -1
  for byte in l:
    i+=1
    if i < number:
      # drop these bytes
      continue
    if len(byte) == 1:
      x.append('0%s' % byte)
    else:
      x.append(byte)
  return x  

with open(FILENAME, 'rb') as f:
  file_contents = f.read()

byte_list = []
trimmed_byte_list = []
for byte in file_contents:
  byte_list.append(hex(ord(byte)).replace('0x', ''))

# trim away the stuff we dont care about
trimmed_byte_list = trim_bytes(byte_list, 12)

rtype = ''.join(trimmed_byte_list[0:2][::-1])
header_size = ''.join(trimmed_byte_list[2:4][::-1])
strings_blocksize = ''.join(trimmed_byte_list[4:8][::-1])
strings_count = ''.join(trimmed_byte_list[8:13][::-1])
#style_count = ''.join(trimmed_byte_list[12:17][::-1])
strings_start = '0x' + ''.join(trimmed_byte_list[20:25][::-1])
#style_start = '0x' + ''.join(trimmed_byte_list[24:29][::-1])


if DEBUG:
  i_header_size = int(header_size, 16)
  print 'Header data:'
  print trimmed_byte_list[:i_header_size]
  print '25 bytes following header_data:'
  print trimmed_byte_list[i_header_size+1:53]

  print 'Type ID: 0x%s' % rtype
  print 'Header size: %d (0x%s)' % (int(header_size, 16), header_size)
  print 'Strings block size is %d bytes (0x%s)' % (int(strings_blocksize, 16), strings_blocksize)

  print '%d strings in file (0x%s)' % (int(strings_count, 16), strings_count)
  #print '%d styles in file (0x%s)' %( int(style_count, 16), style_count)
  print 'Strings begin at offset ' + strings_start
  #print 'Styles begin at offset ' + style_start
  
  if HEADER_ONLY: 
    sys.exit(0)
  

# now trim away this header data
if DEBUG:
  print 'dropping %d bytes...' % int(header_size, 16)

trimmed_bytes = trim_bytes(trimmed_byte_list, int(header_size, 16))

if DEBUG:
  print 'String Data:'
  print trimmed_bytes[:25]

low = 0
high = 4
count = 1
while count < int(strings_count, 16):
#while count < 328:
  index0 = '0x' + ''.join(trimmed_bytes[low:high][::-1])
  index1 = '0x' + ''.join(trimmed_bytes[high:high+4][::-1])

  string0 = hex(int(strings_start, 16) + int(index0,16))
  string1 = hex(int(strings_start, 16) + int(index1,16))
  if DEBUG:
    print index0, index1
    print string0, string1
    print int(string0, 16), int(string1, 16)
  # we actually want to use the data before we cut off the header since the header doesnt give offsets relative to the end of this header

  if DEBUG:
    print trimmed_byte_list[int(string0, 16)+1:int(string1,16)+1] # print the list of bytes that makes up this string
  
  prettyString = ''.join(trimmed_byte_list[int(string0, 16)+1:int(string1,16)+1]).decode('hex').decode('utf-16-be')
  
  # pull off last character
  try:
    if DEBUG:
      print '%d:' % count,
    print prettyString[:-1]
  except UnicodeEncodeError:
    print "this string cannot be decoded."
  
  # increment the key players
  count += 1
  low += 4
  high += 4


# now that we have reached the end of the strings block, up next is a new header
header2_start = int(strings_blocksize, 16)

if DEBUG: 
  print trimmed_byte_list[header2_start:header2_start+20]
htype = '0x'+''.join(trimmed_byte_list[header2_start:header2_start+2][::-1])
hsize = '0x'+''.join(trimmed_byte_list[header2_start:header2_start+20][2:4][::-1])

header2_end = header2_start + int(hsize, 16)
header2 = trimmed_byte_list[header2_start:header2_end]

if DEBUG:
  print 'Header type:', htype
  print 'Header size:', hsize
  print header2
