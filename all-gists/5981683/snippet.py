#! /usr/bin/env python
# A small script for cdp devices discovery

import sys
import pcapy
import socket

from dpkt import ethernet
from dpkt import cdp
from docopt import docopt

__doc__ = """Usage: %s [-h] <interface>

Listens on interface to discover devices emitting cdp packets.

Arguments:
  interface     network interface to listen

Options:
  -h --help
""" %sys.argv[0]


def discover_neighbors (interface, timeout=100):
    def on_cdp_packet (header, data):
        ether_frame = ethernet.Ethernet (data)
        cdp_packet  = ether_frame.cdp

        cdp_info = {}
        for info in cdp_packet.data:
            cdp_info.update ({ info.type: info.data })

        addresses = [socket.inet_ntoa (x.data) for x in cdp_info[cdp.CDP_ADDRESS]]
        print "Hey, %s is at %s." %(cdp_info[cdp.CDP_DEVID], ", ".join (addresses))
    try:
        pcap = pcapy.open_live (interface, 65535, 1, timeout)
        pcap.setfilter ('ether[20:2] == 0x2000') # CDP filter
        
        try:
            while True:
                # this is more responsive to  keyboard interrupts
                pcap.dispatch (1, on_cdp_packet)
        except KeyboardInterrupt, e:
            pass
    except Exception, e:
        print e
    
if __name__ == "__main__" :
    options  = docopt(__doc__)
    discover_neighbors (options['<interface>'])