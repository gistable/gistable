#!/usr/bin/env python
#
# udp_hole_punch_tester.py - UDP Hole Punching test tool
#
# Usage: udp_hole_punch_tester.py remote_host remote_port
#
# Run this script simultaneously on 2 hosts to test if they can punch
# a UDP hole to each other.
#
# * remote_port should be identical on 2 hosts.
# * if remote_port < 1024, must be root.
# * tested on python 2.5.
#
# Copyright (C) 2009 Dmitriy Samovskiy, http://somic.org
#
# License: Apache License, Version 2.0
#          http://www.apache.org/licenses/
#

import sys, os, time, socket, random
from select import select

def log(*args):
    print time.asctime(), ' '.join([str(x) for x in args])

def puncher(remote_host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    my_token = str(random.random())
    log("my_token =", my_token)
    remote_token = "_"

    sock.setblocking(0)
    sock.settimeout(5)

    remote_knows_our_token = False

    for i in range(60):
        r,w,x = select([sock], [sock], [], 0)

        if remote_token != "_" and remote_knows_our_token:
            log("we are done - hole was punched from both ends")
            break

        if r:
            data, addr = sock.recvfrom(1024)
            log("recv:", data)
            if remote_token == "_":
                remote_token = data.split()[0]
                log("remote_token is now", remote_token)
            if len(data.split()) == 3:
                log("remote end signals it knows our token")
                remote_knows_our_token = True

        if w:
            data = "%s %s" % (my_token, remote_token)
            if remote_token != "_": data += " ok"
            log("sending:", data)
            sock.sendto(data, (remote_host, port))
            log("sent", i)
        time.sleep(0.5)

    log("done")
    sock.close()

    return remote_token != "_"

if __name__ == '__main__':
    remote_host = sys.argv[1]
    port = int(sys.argv[2])

    if puncher(remote_host, port):
        log("Punched UDP hole to %s:%d successfully" % (remote_host, port))
    else:
        log("Failed to punch hole")
