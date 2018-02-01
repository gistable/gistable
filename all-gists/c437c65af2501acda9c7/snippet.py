#! /usr/bin/python3

import struct
import sys

def to_int(l, signed=False):
    ret = 0
    for x in l[1:] if signed else l:
        ret = (ret << 1) | x
    if signed and l[0]:
        ret -= pow(2, len(l) - 1)
    return ret

def calc_cksum(p):
    base = 0b1111
    for x in range(4, len(p), 4):
        base += to_int(p[x:x + 4])
    return base & 0b1111

def print_packet(p):
    print(p, end="")
    data = to_int(p[-16:-4], signed=True)
    cks = to_int(p[0:4])
    ecks = calc_cksum(p)
    print("\t%d\t%d\t%d" % (data, cks, ecks), flush=True)

silence = 0
packet = []
while True:
    sample = struct.unpack("h", sys.stdin.buffer.read(2))[0]
    value = False if abs(sample) < 13000 else True
    if value and silence != 0:
        if silence < 150:
            packet.append(0)
        elif silence < 250:
            packet.append(1)
        else:
            if len(packet) == 28:
                print_packet(packet)
            packet.clear()
        silence = 0
    elif not value:
        silence += 1
