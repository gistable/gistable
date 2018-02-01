#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# file: unzip.py
import zipfile,os,sys

if len(sys.argv)==2:
   fname=sys.argv[1]
else:
   print "Usage: python %s filename\n\n" % sys.argv[0]
   sys.exit()

if (not os.path.exists(fname)) or (not zipfile.is_zipfile(fname)):
   print fname,"is not zipfile or not exists"
   sys.exit() 

f=zipfile.ZipFile(fname)
for finfo in f.infolist():
    savename=unicode(finfo.filename,'GBK')
    if os.path.exists(savename):continue
    if finfo.file_size==0:
       os.mkdir(savename)
    else:
       of=open(savename,'w')
       of.write(f.read(finfo))
       of.close()
    print savename
f.close()
