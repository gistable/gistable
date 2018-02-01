#!/usr/bin/python
#@mrexcessive
#this is based on java code from
# https://bitbucket.org/BJRowlett2/tuppers-formula/src/52fcf0b0ee94853e293a6f33e71ccd0c45a6e752/source/Tuppers.java?at=master

import sys,os
from PIL import Image


def GetNextFileName(fnamebase):
   i = 1
   stop = False
   while not stop:
      fname = fnamebase % i
      if not os.path.isfile(fname):
         stop = True
      else:
         i += 1
   return fname


def ReadFilePrintNumber(fname):
   if not os.path.isfile(fname):
      print "ERROR - input file does not exist"
      return
   img = Image.open(fname)
   (width,height) = img.size
   if width <> 106:
      print "ERROR - width must be 106"
      return
   if height <> 17:
      print "ERROR - height must be 17"
      return
   pix = img.load()
   numPixels = width * height
   s = ""
   for i in xrange(0,numPixels):
      x = i / 17
      y = 16 - i % 17
      try:
         (r,g,b) = pix[x,y]
      except ValueError:         # too many values maybe has alpha channel
         (r,g,b,a) = pix[x,y]
      if r+g+b == 0:
         s+="1"
      else:
         s+="0"
   num = int(s,2)
   num *= 17
   print num


def ReadNumberWriteFile(num):
   fname = GetNextFileName("tuppers%i.png")
   num = int(num) / 17
   binstr = bin(num)[2:]      # drop the leading '0b'
      while len(binstr) < 1802:
      binstr = "0" + binstr
#   	String binary = decimal.toString(2);
#		binary = String.format("%1802s", binary);
#		binary = binary.replace(' ', '0');
   img = Image.new("RGB", (106,17), "white")
   pix = img.load()
   for i in xrange(0,len(binstr)):
      if binstr[i] == "1":
         pix[i/17,16-(i%17)] = (0,0,0)
   img.save(fname)
   img.show()


if __name__ == "__main__":
   if len(sys.argv) == 3:
      command = sys.argv[1].lower().strip()
      if command == "read":
         ReadFilePrintNumber(sys.argv[2])
      elif command == "write":
         ReadNumberWriteFile(sys.argv[2])
   else:
      print "Usage:"
      print "  %s read <file>" % sys.argv[0]
      print "  will print out the Tupper number for the image file"
      print "or"
      print "  %s write num" % sys.argv[0]
      print "  will create a file called TupperN.png"
      print "  the next available N will be used, so 0,1,2,3 etc."
