#!/usr/bin/env python2
try:
    import scapy.all as scapy
except ImportError:
    import scapy

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog=__file__,
        description="Proof of concept for wireshark replacement",
        version="%(prog)s v0.0.1 by Brian Wallace (@botnet_hunter)",
        epilog="%(prog)s v0.0.1 by Brian Wallace (@botnet_hunter)"
    )
    parser.add_argument('path', metavar='path', type=str, nargs='*', default=None, help="Paths to files to parse")

    args = parser.parse_args()

    for p in args.path:
        pcap = scapy.rdpcap(p)

        for packet in pcap:
            print packet.show()
