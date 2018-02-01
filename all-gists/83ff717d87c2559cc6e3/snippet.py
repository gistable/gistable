#!/usr/bin/env python2.7

import sys, binascii, subprocess
import dpkt, pcap, socket

cottonelle = 'f0272d8b52c0'

def main():
    name = pcap.lookupdev()
    try:
        pc = pcap.pcap(name)
    except:
        print pc.geterr()

    try:
        print 'listening on %s' % (pc.name)
        for ts, pkt in pc:
            eth = dpkt.ethernet.Ethernet(pkt)
            ip_hdr = eth.data
            if eth.type != dpkt.ethernet.ETH_TYPE_ARP:
                continue
            if binascii.hexlify(eth.src) == cottonelle:
                subprocess.call("/usr/local/bin/stopsim", shell=True)
    except Exception as e:
        print e, pc.geterr()

if __name__ == '__main__':
    main()