#!/usr/bin/env python

import logging
from scapy.all import *
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

fakeip = ["4.36.66.178", "8.7.198.45", "37.61.54.158", "46.82.174.68", "59.24.3.173", "64.33.88.161", "64.33.99.47", "64.66.163.251", "65.104.202.252", "65.160.219.113", "66.45.252.237", "72.14.205.104", "72.14.205.99", "78.16.49.15", "93.46.8.89", "128.121.126.139", "159.106.121.75", "169.132.13.103", "192.67.198.6", "202.106.1.2", "202.181.7.85", "203.161.230.171", "207.12.88.98", "208.56.31.43", "209.145.54.50", "209.220.30.174", "209.36.73.33", "211.94.66.147", "213.169.251.35", "216.221.188.182", "216.234.179.13"]
testdomain = ["twitter.com", "facebook.com", "youtube.com"]
dnshost = "8.8.8.8"
for h in testdomain:
    prehost = ''
    for i in range(5,25):
        resp = sr1(IP(dst=dnshost,ttl=i)/UDP()/DNS(rd=1,qd=DNSQR(qname=h)), verbose=False)
        data = resp.payload.payload
        if isinstance(data, DNS) and "an" in data.fields and "rdata" in data.an.fields:
            if data.an.rdata in fakeip:
                print "Warnning: GFW is detected, behind [%s], HOP=%d, Test Domain=[%s]" % (prehost, i, h)
                break
        else:
            prehost = resp.src