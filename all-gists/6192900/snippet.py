#! /usr/bin/env python

# Set log level to benefit from Scapy warnings
import logging
logging.getLogger("scapy").setLevel(1)

from scapy.all import *

if __name__ == "__main__":
	hosts 	= raw_input('Hostnames you would like to traceroute sepearated by a comma: ')
	ttl 	= raw_input("Time To Live: ")
	if not ttl: ttl = 20
	traceroute([x.strip() for x in hosts.split(',')],maxttl=ttl)