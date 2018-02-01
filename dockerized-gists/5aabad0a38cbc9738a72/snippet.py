#!/usr/bin/env python

import time
import sys

last_rx = 0
last_tx = 0
first_time = True

def print_bps(iface, line):
    tmp = line.split()

    global last_rx, last_tx, first_time

    name = tmp[0].replace(":", "")
    if iface == name:
        if not first_time:
            rx = int(tmp[1]) - last_rx
            tx = int(tmp[9]) - last_tx

            rx = rx if rx >= 0 else 0
            tx = tx if tx >= 0 else 0

            print "%-15s%-15d%-15d%-15d%-15d" % (name, rx, rx * 8, tx, tx * 8)

        last_rx = int(tmp[1])
        last_tx = int(tmp[9])
        first_time = False

def read_file(iface):
    with open("/proc/net/dev") as f:
        lines  = f.readlines()
        for line in lines[2:]:
            print_bps(iface, line)
        time.sleep(1)

def read_forever(iface):
    print "%-15s%-15s%-15s%-15s%-15s" % ("iface", "rx(byte)", "rx(bit)", "tx(byte)", "tx(bit)")
    while True:
        read_file(iface)

def usage():
    print "usage: %prog [interface name]"
    sys.exit(0)

if __name__ == "__main__":
    iface = None

    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            usage()
        else:
            iface = sys.argv[1]
    else:
        usage()

    read_forever(iface)


