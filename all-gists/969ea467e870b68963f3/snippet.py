#!/usr/bin/env python
# encoding: utf-8
# 2014 - Neal Shyam [@nealrs | nealshyam.com]
# usage: $python checkrap.py first_name last_name domain_name
# e.g:   $python checkrap.py john doe gmail.com 
#
#
# PLEASE DON'T BE A DICK OR USE THIS FOR EVIL.
# Seriously, the internet is a nice place, let's keep it that way.

import sys
import time
from rapportive import rapportive # https://github.com/jordan-wright/rapportive

fn = sys.argv[1]
ln = sys.argv[2]
d = sys.argv[3]

fi = fn[:1]
li = ln[:1]
p1 = fn  # neal
p2 = ln	# shyam
p3 = fi+li # ns
p4 = fn+"_"+ln # neal_shyam
p5 = fi+"_"+ln # n_shyam_
p6 = fn+ln # nealshyam
p7 = fn+"."+ln # neal.shyam
p8 = fn+li # neals
p9 = fi+ln # nshyam
p10 = fn+"."+li # neal.s
p11 = fi+"."+ln # n.shyam
p12 = ln+"."+fn # shyam.neal
p13 = ln+fi # shyamn
p = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13]

e = iter(p)
print '\033[95m'+"Checking with Rapportive..."+'\033[0m'
for x in e:
 time.sleep(2) # 2 second timeout, you may need to play with this. 
 i = x+"@"+d
 r = rapportive.request(i)
 print i,"::",r
print '\033[95m'+"Done"+'\033[0m'