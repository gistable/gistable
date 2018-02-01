from collections import OrderedDict
import argparse
import logging

# Suppress ipv6 warning when importing scapy
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import IP, UDP, send, L3RawSocket, conf


PACKET_FORMAT = "tag=%s&%s&seq=0x%04x"

# Set up argument parser
p = argparse.ArgumentParser()
args = OrderedDict([
    ("rfid_tag", {"help": "The RFID tag to send eg. abcdef12345678"}),
    ("--dest_ip", {"help": "Destination IP - defaults to broadcast", "default": "255.255.255.255"}),
    ("--source_ip", {
        "help": "The IP to pretend to be when sending the swipe - defaults to own IP",
        "default": None}),
    ("--direction", {
        "help": "'in' or 'out' means RFID card presented, or taken away",
        "choices": ("in", "out"), "default": "in"}),
    ("--seq_number", {"help": "Sequence number to start on", "default": 1, "type": int}),
    ("--port", {"help": "Destination port", "default": 11000, "type": int}),
    ("--count", {"help": "How many packets to send", "default": 1, "type": int}),
    ("--loop", {"help": "Send forever", "action": "store_true"}),
    ("--incr_seq", {"help": "Increment the seq number on each packet", "action": "store_true"})
])
for arg, opts in args.items():
    p.add_argument(arg, **opts)

if __name__ == "__main__":
    args = p.parse_args()

    count = 0

    try:
        if args.dest_ip in ("127.0.0.1", "localhost"):
            conf.L3socket = L3RawSocket

        ip = IP(dst=args.dest_ip)
        if args.source_ip is not None:
            ip.src = args.source_ip

        udp = UDP(dport=args.port)

        if args.incr_seq:
            seq = args.seq_number

            if args.loop:
                while True:
                    pkt = ip/udp/(
                        PACKET_FORMAT % (args.rfid_tag, args.direction, seq))
                    send(pkt)
                    count += 1
                    seq += 1
            else:
                i = 0
                while i < args.count:
                    pkt = ip/udp/(
                        PACKET_FORMAT % (args.rfid_tag, args.direction, seq))
                    send(pkt)
                    count += 1
                    seq += 1
                    i += 1

        else:
            pkt = ip/udp/(
                PACKET_FORMAT % (args.rfid_tag, args.direction, args.seq_number))

            if args.loop:
                send(pkt, loop=args.loop)
                count = -1
            else:
                send(pkt, count=args.count)
                count = -1
    finally:
        if count > -1:
            print "Sent %d packets." % count
