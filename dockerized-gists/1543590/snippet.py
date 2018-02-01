'''
  Computes SQuare RooT in Python SQRT

  s = (s+nr/s)1/2
  Twitter     : http://twitter.com/thinkphp
  Website     : http://thinkphp.ro
  Google Plus : http://gplus.to/thinkphp
  MIT Style License
'''

import math
import sys

def sqrt(n):
      if n < 0: return "Value Error: math domain error"
      if n == 0: return 0 
      s = 1
      for i in range(1,1000):
          s = (s + float(n/s))*1.0/2.0
      return s

if __name__ == "__main__":
   if len(sys.argv) != 2:
      print "Usage: python sqrt.py n"
      sys.exit()    
   n = float(sys.argv[1])
   print "sqrt(",n,") = ", math.sqrt(n), " defined by the C Standard"
   print "sqrt(",n,") = ", sqrt(n), " defined by Adrian"