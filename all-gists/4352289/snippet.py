# GPLv2+, by fcicq
# from http://www.hpl.hp.com/techreports/98/HPL-98-135.pdf
IRRED_COEFF = [
  4,3,1,5,3,1,4,3,1,7,3,2,5,4,3,5,3,2,7,4,2,4,3,1,10,9,3,9,4,2,7,6,2,10,9,
  6,4,3,1,5,4,3,4,3,1,7,2,1,5,3,2,7,4,2,6,3,2,5,3,2,15,3,2,11,3,2,9,8,7,7,
  2,1,5,3,2,9,3,1,7,3,1,9,8,3,9,4,2,8,5,3,15,14,10,10,5,2,9,6,2,9,3,2,9,5,
  2,11,10,1,7,3,2,11,2,1,9,7,4,4,3,1,8,3,1,7,4,1,7,2,1,13,11,6,5,3,2,7,3,2,
  8,7,5,12,3,2,13,10,6,5,3,2,5,3,2,9,5,2,9,7,2,13,4,3,4,3,1,11,6,4,18,9,6,
  19,18,13,11,3,2,15,9,6,4,3,1,16,5,2,15,14,6,8,5,2,15,11,2,11,6,2,7,5,3,8,
  3,1,19,16,9,11,9,6,15,7,6,13,4,3,14,13,3,13,6,3,9,5,2,19,13,6,19,10,3,11,
  6,5,9,2,1,14,3,2,13,3,1,7,5,4,11,9,8,11,6,5,23,16,9,19,14,6,23,10,2,8,3,
  2,5,4,3,9,6,4,4,3,2,13,8,6,13,11,1,13,10,3,11,6,5,19,17,4,15,14,7,13,9,6,
  9,7,3,9,7,1,14,3,2,11,8,2,11,6,4,13,5,2,11,5,1,11,4,1,19,10,3,21,10,6,13,
  3,1,15,7,5,19,18,10,7,5,3,12,7,2,7,5,1,14,9,6,10,3,2,15,13,12,12,11,9,16,
  9,7,12,9,3,9,5,2,17,10,6,24,9,3,17,15,13,5,4,3,19,17,8,15,6,3,19,6,1]

def getpoly(deg):
  if deg & 7 != 0 or deg < 8 or deg > 1024: raise Exception('Not supported Degree')
  x = deg / 8 - 1
  return (1<<IRRED_COEFF[3*x]) + (1<<IRRED_COEFF[3*x + 1]) + (1<<IRRED_COEFF[3*x + 2]) + 1

def gadd(a, b): # minus is the same
  return a ^ b

def gmul(a, b, deg=8):
  poly = getpoly(deg)
  max_1 = (1<<deg) - 1
  max_2 = 1<<(deg - 1)
  z = 0
  if a & 1:
    r = b
  else:
    r = 0
  for i in xrange(1,deg+1):
    mark = b & max_2
    b = (b << 1) & max_1
    if mark: # Note: not really protected by timing attack. since...
      b ^= poly
    else:
      b ^= z
    # print a & (1 << i), r, b
    if a & (1 << i):
      r ^= b
    else:
      r ^= z
  return r

# py2.7+. may need to change this.
def nlen(n):
 # alternate: len(bin(n))-2 for positive
 return n.bit_length()

def ginv(x, deg=8):
  u = x
  v = (1<<deg) + getpoly(deg)
  x = 1
  y = 0
  while u:
    i = nlen(u) - nlen(v)
    if i < 0:
      u,v = v,u
      x,y = y,x
      i = -i
    u ^= (v << i)
    x ^= (y << i)
  return y

if __name__ == "__main__":
  print gmul(3,7) == 9
  print gmul(7,3) == 9
  print ginv(0x53) == 0xCA
  print ginv(0xCA) == 0x53