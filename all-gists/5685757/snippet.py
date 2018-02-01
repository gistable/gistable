#!/usr/bin/python
# -*- coding: utf-8 -*-

#Script for reverting ZFS changes by destroying uberblocks
#Author: Martin Vool
#E-mail: mardicas@gmail.com
#Version: 0.1
#Date: 16 November 2009


import time
import subprocess
import sys
import os
#Default blocksize
bs=512
#default total blocks (sorry programming in estonian :-/)
suurus=None

if len(sys.argv) > 2:
    for arg in sys.argv:
        arg=arg.split('=')
        if len(arg) == 1:
            file=arg[0]
        elif arg[0] == '-bs':
            bs=int(arg[1])
        elif arg[0] == '-tb':
            suurus=int(arg[1])
else:
    print 'Usage: zfs_revert.py [-bs=n default:n=512 blocksize] \\n [-tb=n total block size in blocks] [file/device] You have to set -tb'
    exit(1)
print int(bs)
if suurus == None:
    print 'Total block size in blocks is undefined'
    exit(1)
#make solaris use gnu grep.
if os.uname()[0] == 'SunOS':
    grep_cmd='ggrep'
else:
    grep_cmd='grep'


#to format program output
def formatstd(inp):
    inp=inp.split('\n')
    ret=[]
    for line in inp:
        columns=line.split(' ')
        nc=[]
        for c in columns:
            if c != '':
                nc.append(c)
        ret.append(nc)
    return ret


#read blocks from beginning(64mb)
a_count=(256*bs)
#read blocks from end (64mb)
l_skip=suurus-(256*bs)


print 'Total of %s blocks'%suurus
print 'Reading from the beginning to %s blocks'%a_count
print 'Reading from %s blocks to the end'%l_skip

#get the uberblocks from the beginning and end
yberblocks_a=formatstd(subprocess.Popen('sync && dd bs=%s if=%s count=%s | od -A x -x | %s -A 2 "b10c 00ba" | %s -v "\-\-"'%(bs,file, a_count,grep_cmd,grep_cmd), shell=True, stdout=subprocess.PIPE).communicate()[0])
yberblocks_l=formatstd(subprocess.Popen('sync && dd bs=%s if=%s skip=%s | od -A x -x | %s -A 2 "b10c 00ba" | %s -v "\-\-"'%(bs,file, l_skip,grep_cmd,grep_cmd), shell=True, stdout=subprocess.PIPE).communicate()[0])


yberblocks=[]

for p in yberblocks_a:
    if len(p) > 0:
        #format the hex address to decmal so dd would eat it.
        p[0]=(int(p[0], 16)/bs)
        yberblocks.append(p)

for p in yberblocks_l:
    if len(p) > 0:
        #format the hex address to decmal so dd would eat it and add the skipped part.
        p[0]=((int(p[0], 16)/bs)+int(l_skip)) #we have to add until the place we skipped so the adresses would mach.
        yberblocks.append(p)
print '----'
#here will be kept the output that you will see later(TXG, timestamp and the adresses, should be 4, might be less)
koik={}
i=0
for p in yberblocks:
    if len(p) > 0:
        if i == 0:#the first output line
            address=p[0]
        elif i == 1:#second output line
            #this is the output of od that is in hex and needs to be reversed
            txg=int(p[4]+p[3]+p[2]+p[1], 16)
        elif i == 2:#third output line
            timestamp=int(p[4]+p[3]+p[2]+p[1], 16)
            try:
                aeg=time.strftime("%d %b %Y %H:%M:%S", time.localtime(timestamp))
            except:
                aeg='none'
            if koik.has_key(txg):
                koik[txg]['addresses'].append(address)
            else:
                koik[txg]={
                    'txg':txg,
                    'timestamp':timestamp,
                    'htime': aeg,
                    'addresses':[address]
                }
        if i == 2:
            i=0
        else:
            i+=1
    keys = koik.keys()
    keys.sort()
    
while True:
    keys = koik.keys()
    keys.sort()
    print 'TXG\tTIME\tTIMESTAMP\tBLOCK ADDRESSES'
    for k in keys:
        print '%s\t%s\t%s\t%s'%(k, koik[k]['htime'],koik[k]['timestamp'],koik[k]['addresses'])
    try:
        save_txg=int(input('What is the last TXG you wish to keep?\n'))
        keys = koik.keys()
        keys.sort()
        for k in keys:
            if k > save_txg:
                for adress in koik[k]['addresses']:
                    #wrtie zeroes to the unwanted uberblocks
                    format=formatstd(subprocess.Popen('dd bs=%s if=/dev/zero of=%s seek=%s count=1 conv=notrunc'%(bs, file, adress), shell=True, stdout=subprocess.PIPE).communicate()[0])
                del(koik[k])
        #sync changes to disc!
        sync=formatstd(subprocess.Popen('sync', shell=True, stdout=subprocess.PIPE).communicate()[0])
    except:
        print ''
        break