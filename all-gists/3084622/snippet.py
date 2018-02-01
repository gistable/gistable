#!/usr/bin/env python

import sys, struct, binascii

def header(bytes): 
   return struct.unpack('>NNccccc', bytes)

def parse(bytes): 
   signature = bytes[:8]
   bytes = bytes[8:]

   while bytes: 
      length = struct.unpack('>I', bytes[:4])[0]
      bytes = bytes[4:]

      chunk_type = bytes[:4]
      bytes = bytes[4:]

      chunk_data = bytes[:length]
      bytes = bytes[length:]

      crc = struct.unpack('>I', bytes[:4])[0]
      bytes = bytes[4:]

      print length, chunk_type, len(chunk_data), repr(crc)
      yield chunk_type, chunk_data

def chunk(chunk_type, chunk_data): 
   length = struct.pack('>I', len(chunk_data))
   c = binascii.crc32(chunk_type + chunk_data) & 0xffffffff
   crc = struct.pack('>I', c)
   print len(chunk_data), chunk_type, len(chunk_data), c
   return length + chunk_type + chunk_data + crc

def main(): 
   name = sys.argv[1]
   with open(name, 'rb') as f: 
      bytes = f.read()

   for a, b in parse(bytes):
      print a, repr(b)

if __name__ == '__main__': 
   main()
