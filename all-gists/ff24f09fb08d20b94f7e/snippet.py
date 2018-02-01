#!/usr/bin/python
# -*- coding: utf-8 -*-  
#from http://www.jianshu.com/p/f4cabcb17e8e

def GetLists(subdomain,start,end):
    ret = []
    for i in xrange(int(start),int(end)+1):
        ret.append(subdomain+str(i)+'.dropbox.com')
    return ret

def GetDlClientLists():
    return GetLists('dl-client',1,999)

def GetDlDebugLists():
    return GetLists('dl-debug',1,40)

def GetClientLists():
    return GetLists('client',1,99)

def GetNotifyLists():
    return GetLists('notify',1,10)

hosts = []
hosts.extend([
        'dropbox.com',
        'www.dropbox.com',
        'forums.dropbox.com',
        'dl.dropboxusercontent.com',
        'd.dropbox.com',
        'client-lb.dropbox.com'
        ])
hosts.extend(GetDlClientLists())
hosts.extend(GetDlDebugLists())
hosts.extend(GetClientLists())
hosts.extend(GetNotifyLists())

import subprocess
for h in hosts:
    cmd = 'nslookup -vc ' + h + ' 8.8.8.8'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    valid = False
    for line in p.stdout.readlines():
        if line.startswith('Non-authoritative answer:'):
            valid = True
        elif valid and line.startswith('Address:'):
            ip = line.replace('Address: ','').replace('\n','')
            print ip + ' ' + h