'''        
          x
  f(x) = e  - a
  if f(0)*f(a) < 0  then exists the solution (0,a] 
'''
import math
import sys

def loge(n,li,ls):
    if math.fabs(li-ls) <= 0.000001:
       return (li+ls)/2.0
    if (math.exp(li)-n)*(math.exp((li+ls)/2.0)-n) < 0:
       return loge(n,li,(li+ls)/2.0)
    else:
       return loge(n,(li+ls)/2.0,ls)

def ln(n):
    if n == 0 or n < 0:
       return "Math Domain Error"
    if n == 1:
       return 0
    if n > 0 and n < 1:
       return loge(n,0,-n-80)
    else:
       return loge(n,0,n)

if __name__ == "__main__":
   if len(sys.argv) != 2:
      print "Usage: python ln.py 5"
   else:
      n = float(sys.argv[1])
      print "LN(",n,"):",ln(n)
      print "LN(",n,"):",math.log(n)
