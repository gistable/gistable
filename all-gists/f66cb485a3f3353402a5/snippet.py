#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import pcap #requires the python-libpcap module

def libpcap_net_data(cap_file, net_iface, filter_expr=None):
    """A decorator that can be used to sniff network data for the duration of a function call
    if there is heavy traffic on the network interface the captured data will contain spurious packets
    not related to the function call
    
    cap_file is the pcap filename where the captured data will be writtend
    net_iface is the network interface to sniff
    filter_expr is an optional filter expression: `man pcap-filter` for more info"""
    def _libpcap_net_data(func):
        def wrap(*args, **kwargs):
            #Start a libpcap object
            print "Start libpcap listen on %s writing to %s" % (net_iface, cap_file)
            p = pcap.pcapObject()
            p.open_live(net_iface, 65535, 0, 100)
            p.dump_open(cap_file)
            if filter_expr is not None:
                p.setfilter(filter_expr, 0, 0)
            
            res = func(*args,**kwargs)
            #Stop the tcpdump subprocess
            print "Stopping libpcap process on %s" % (cap_file,)
            p.dispatch(0, None)
            return res
        return wrap
    return _libpcap_net_data

#This will sniff only dns info on wlan0 and write it to myPackets.cap file
@libpcap_net_data('myPackets.cap','wlan0','port 53')
def libpcap_do_request(url):
    h1 = urllib2.urlopen(url).read()
    return h1

if __name__ == '__main__':
    url = 'http://www.example.com'
    res = libpcap_do_request(url)