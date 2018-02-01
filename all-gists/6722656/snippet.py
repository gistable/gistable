#!/usr/bin/env python
# encoding: utf-8
 
# install dependencies: sudo pip install validate_email pyDNS
# run it: python check.py robin hood gmail.com

# FYI, forwarding addresses (not catchalls) will report 'probably not valid'. that's all i've got right now.

import sys
from validate_email import validate_email 

# define name, domain, and initials parameters
fn = sys.argv[1]
ln = sys.argv[2]
d = sys.argv[3]
fi = fn[:1]
li = ln[:1]

# define email patterns
p0 = "xxx" #catchall trigger
p1 = fn  # robin
p2 = ln # hood
p3 = fi+li # rh
p4 = fn+"_"+ln # robin_hood
p5 = fi+"_"+ln # r_hood
p6 = fn+ln # robinhood
p7 = fn+"."+ln # robin.hood
p8 = fn+li # robinh
p9 = fi+ln # rhood
p10 = fn+"."+li # robin.h
p11 = fi+"."+ln # r.hood
p12 = ln+"."+fn # hood.robin
p13 = ln+fi # hoodr

# add a splash of color
HEAD = '\033[95m'
OK = '\033[92m'
WARN = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

p = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13]
e = iter(p)

# run validation logic
print HEAD+"Checking..."+ENDC
for x in e:
 i = x+"@"+d
 has_mx = validate_email(i,check_mx=True)
 is_real = validate_email(i,verify=True)
 
 if (has_mx == False):
  print FAIL+"no mx record"+ENDC
  break
 elif (is_real and x == p0):
  print WARN+"catchall detected"+ENDC
  break
 elif (x != p0):
  print i,
  if is_real:
   print ": "+OK+"probably valid"+ENDC
  else:
   print ": probably not valid"
print HEAD+"Done"+ENDC