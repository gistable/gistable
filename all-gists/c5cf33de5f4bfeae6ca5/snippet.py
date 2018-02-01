#! /usr/bin/env/python

from scapy.all import *
import binascii

def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        if pkt.addr2 == 'cc:c3:xx:xx:xx:xx':
            print(-(256-int.from_bytes(pkt.notdecoded[-4:-3], byteorder='big')))


if __name__ == '__main__':
    sniff(iface='wlan0mon', prn = PacketHandler)