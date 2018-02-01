#!/usr/bin/env python
"""
Sniff a specific port for Bit Torrent DHT traffic and print
requests/responses in human readable form.

Reference: http://www.bittorrent.org/beps/bep_0005.html
"""

from pcapy import open_live
from bencode import bdecode
from socket import inet_aton, inet_ntoa
import dpkt
import sys

# Defaults to 51413 (transmission's default port)
filter_port = 51413

# Callback function for parsing packets
def parse_udp(hdr, data):
    global filter_port 
    try:
        eth = dpkt.ethernet.Ethernet(data)
    except Exception:
        return
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        return

    ip = eth.data
    if ip.p == dpkt.ip.IP_PROTO_UDP and filter_port in (ip.data.dport, ip.data.sport):
        payload = ip.data.data
    else:
        return

    # Print plain text bencoded request.
    try:
        data = bdecode(payload)
        print "%s:%d -> %s:%d (%d bytes): %s\n" % (inet_ntoa(ip.src), ip.data.sport, 
		inet_ntoa(ip.dst), ip.data.dport, len(payload), data)
    except Exception:
        return

def main(argv):
    global filter_port 

    if len(argv) == 1:
        try:
            filter_port = int(argv[0])
        except ValueError:
            print "Invalid port number"
            sys.exit(1)

    print "[+] Starting sniffer"
    pcap_obj = open_live("eth0", 65536, False, True)
    try:
        pcap_obj.loop(-1, parse_udp)
    except KeyboardInterrupt:
        print "[!] Exiting"
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
