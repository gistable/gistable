#!/usr/bin/env python
"""
Logging part of a multicast group scanner.

Needs to be run with capabilities allowing it to read
raw data from the network interface. (usually root)

Author: Lasse Karstensen <lasse.karstensen@gmail.com>, April 2013.
"""
import sys
import socket
import pcapy
import impacket
import datetime
from impacket.ImpactDecoder import EthDecoder, UDPDecoder, IPDecoder
from time import time
from pprint import pprint

INTERFACE = "eth0"
REPORT_EVERY = 4  # seconds

# List of dst-ports that pcap should filter out for us.
SKIPLIST = [
    67,
    137,
    138,
    5353,  # mdns
    5355,
    9875,  # SAP announcements
    17500,
    57621,
]

bintime = time()
state = {}

def print_report():
    global state
    now = datetime.datetime.now().isoformat()
    for k, v in state.items():
        if v > 1e3:
            print "%s\t%s\t%i" % (now, k, v)
    sys.stdout.flush()

def recv_packet(hdr, data):
    global bintime
    global state

    frame = EthDecoder().decode(data)
    ip = frame.child()
    udp = ip.child()
    key = ip.get_ip_dst() + "__%s" % udp.get_uh_dport()

    try:
        state[key] += ip.get_ip_len()
    except KeyError:
        state[key] = ip.get_ip_len()

    now = time()
    if (bintime + REPORT_EVERY) < now:
        bintime = now
        print_report()
        state = {}


def main():
    if 1:
        s = pcapy.open_live(INTERFACE, 1500, True, 10)
    else:
        s = pcapy.open_offline("mcast.pcap")

    pcapfilter = "ip proto \udp and multicast"
    for p in SKIPLIST:
        pcapfilter += " and port not %i" % p

    s.setfilter(pcapfilter)
    s.loop(-1, recv_packet)

if __name__ == "__main__":
    main()