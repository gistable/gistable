#!/usr/bin/python
#Matthew Wollenweber
#mjw@cyberwart.com

import math
from numpy import zeros
from time import time
from random import randint

#from http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html
def H(data): 
  if not data: 
    return 0 
  
  entropy = 0 
  for x in range(256): 
    p_x = float(data.count(chr(x)))/len(data) 
    if p_x > 0: 
      entropy += - p_x*math.log(p_x, 2) 
  return entropy

def Fast_H(data):
  if not data:
    return 0
  
  entropy = 0
  len_data = len(data)
  data_counts = zeros(256)
  
  for d in data:
    data_counts[ord(d)] += 1
  
  for x in range(0, 256):
    p_x = float(data_counts[x])/len_data 
    
    if p_x > 0: 
      entropy += - p_x*math.log(p_x, 2) 
  return entropy

def main():
  dt = [-1.0, -1.0]
  data = []
  for i in range (0, 100000):
    data.append(chr(randint(0, 255)))
  
  t = time()
  print "entropy = %s" % H(data)
  dt[0] = time() - t
  
  t = time()
  print "fast_entropy = %s" % Fast_H(data)
  dt[1] = time() - t
  
  print "H() too %f Fast_H took %f" % (dt[0], dt[1])
  
if __name__ == "__main__":
  main()
