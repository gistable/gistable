#!/usr/bin/env python

# check_peer_interfaces.py
# Author: David Wittman <david@wittman.com>
#
# Checks to see if two interfaces are on the same network by sending a
# unique broadcast packet out of the first interface and listening for that
# packet on the second interface.
#
# Assumes that you're running a Linux variant, and that both interfaces
# provided are administratively up.
#
# Based on bonding.py by Matt Martz

import fcntl
import os
import socket
import struct
import sys

# asm/sockios.h
SO_BINDTODEVICE = 25

# sockios.h
SIOCGIFFLAGS = 0x8913          # get flags
SIOCSIFFLAGS = 0x8914          # set flags
SIOCGIFHWADDR = 0x8927         # Get hardware address

# net/if.h
IFF_PROMISC = 0x100            # Receive all packets.


def get_mac_addr(iface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return fcntl.ioctl(
        s.fileno(),
        SIOCGIFHWADDR,
        struct.pack('256s', iface[:15])
    )[18:24]


def are_peers(send_iface, recv_iface):
    # Create a unique payload to match against later
    identifier = 'IF%sIF' % send_iface
    payload = '%s%s' % (identifier, os.urandom(46 - len(identifier)))

    src_mac = get_mac_addr(send_iface)
    # broadcast address
    dest_mac = ('f' * 12).decode('hex')
    # use an unregistered ethertype for peer discovery
    frame_type = '\x50\x44'
    frame_type_int = int(frame_type.encode('hex'), 16)

    # Configure socket on send interface
    send_sock = socket.socket(
        socket.AF_PACKET, socket.SOCK_RAW,
        socket.htons(frame_type_int)
    )
    send_sock.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, send_iface + '\0')
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_sock.bind((send_iface, 0))
    send_sock.setblocking(0)

    # Configure socket on receive interface
    recv_sock = socket.socket(
        socket.AF_PACKET, socket.SOCK_RAW,
        socket.htons(frame_type_int)
    )
    recv_sock.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, recv_iface + '\0')
    recv_sock.bind((recv_iface, 0))
    recv_sock.settimeout(0.5)

    # Put receive socket in promiscuous mode
    current_flags = 0
    ifreq = fcntl.ioctl(
        recv_sock.fileno(),
        SIOCGIFFLAGS,
        struct.pack('256s', recv_iface[:15])
    )
    (current_flags,) = struct.unpack('16xH', ifreq[:18])
    current_flags |= IFF_PROMISC
    ifreq = struct.pack('16sH', recv_iface, current_flags)
    fcntl.ioctl(recv_sock.fileno(), SIOCSIFFLAGS, ifreq)

    for _ in xrange(3):
        try:
            packet = ''.join([dest_mac, src_mac, frame_type, payload])
            send_sock.sendall(packet)
            data = recv_sock.recv(60)
        except (socket.timeout, socket.error):
            continue

        recv_frame_type = data[12:14]
        recv_payload = data[14:]

        if payload == recv_payload and frame_type == recv_frame_type:
            peers = True
            break
    else:
        peers = False

    # Take receiving interface out of promiscuous mode
    current_flags ^= IFF_PROMISC
    ifreq = struct.pack('16sH', recv_iface, current_flags)
    fcntl.ioctl(recv_sock.fileno(), SIOCSIFFLAGS, ifreq)

    recv_sock.close()
    send_sock.close()

    return peers


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: %s <iface> <iface>\n" % sys.argv[0])
        sys.stderr.flush()
        sys.exit(2)

    send_iface = sys.argv[1]
    recv_iface = sys.argv[2]

    if are_peers(send_iface, recv_iface):
        print "SUCCESS! %s and %s are peers" % (send_iface, recv_iface)
    else:
        print "FAIL! %s and %s are not peers" % (send_iface, recv_iface)
        sys.exit(1)

if __name__ == '__main__':
    main()