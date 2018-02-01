#!/usr/local/bin/python
from pyPdf import PdfFileWriter, PdfFileReader
import random
from pprint import pprint as pp
import sys
# sys.setrecursionlimit(10000000)

seed = 'BN9F'
pile = [1]
def getNumber():
  n = random.randint(1, 8)
  if( n == 1 or n == 8 or n == 4 ):
    return n
  else:
    return getNumber()
def generateRandom():
  v = str(getNumber()) + str(getNumber()) + str(getNumber()) + str(getNumber())
  ind = pile.index(v) if v in pile else False
  if (ind == False):
    pile.append(v)
    return v
  else:
    return generateRandom()
def decryptPdf(f):
  if(f.getIsEncrypted()):
    ran = generateRandom()
    t = f.decrypt(seed+ran)
    if (t==1):
      return {'pdf': f, 'r': ran, 's': seed+ran}
    else:
      return decryptPdf(f)
  else:
    print 'cola'
    return f.getDocumentInfo().title

f = PdfFileReader(file("EstadodeCuenta.pdf", "rb"))
o = decryptPdf(f)
ff = o.get('pdf')
ff.decrypt(o.get('s'))
print ff.getIsEncrypted()
print "title = %s" % (f.getDocumentInfo().title)
pp(o)