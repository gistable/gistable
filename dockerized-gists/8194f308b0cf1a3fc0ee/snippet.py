#!/usr/bin/python
"""
Multicast group scanner.

Author: Lasse Karstensen <lasse.karstensen@gmail.com>, November 2014
"""
import gevent
from gevent import monkey
monkey.patch_all()

from gevent.queue import JoinableQueue

import socket
import logging
from random import random, shuffle
from sys import argv
from struct import pack
from os import uname
from time import sleep

from netaddr import IPNetwork

completed = 0
PER_GROUP_LISTEN_TIME = 10  # seconds
#CONCURRENT_GROUPS = 10
CONCURRENT_GROUPS = 4

def join(group):
    interface_ip = "SET-YOUR-ETH0-IP-HERE"  # Hard coded is the best.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(5)
    sock.bind((group, 1234))
    sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
                    socket.inet_aton(interface_ip))
    mreq = pack('4sl', socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def multicast_scopes():
    scopes = [
        IPNetwork("224.0.2.0/16"),   # AD-HOC block
        IPNetwork("224.3.0.0/15"),
        IPNetwork("233.252.0.0/14"),
        IPNetwork("239.0.0.0/8")  # private scope
    ]
    shuffle(scopes)
    for scope in scopes:
        for ip in scope:
            yield ip
            #print ip

def poolworker(q):
    global completed
    sleep(random()*5)  # Spread them out.
    while True:
        try:
            group = q.get(timeout=10)
        except gevent.queue.Empty:
            break
        logging.info("Joining %s" % group)
        sock = join(str(group))
        sleep(PER_GROUP_LISTEN_TIME)
        completed += 1
        logging.info("Parting %s. (%i done in this run)", group, completed)
        sock.close()
        q.task_done()

def feeder(q):
    for group in multicast_scopes():
        #logging.debug("putting %s" % group)
        q.put(group)
        if q.qsize() > 1000:
            sleep(5)

def main():
    if "-v" in argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    logging.info("Starting up")

    q = JoinableQueue()
    gevent.spawn(feeder, q)

    tasks = []
    for x in range(0, CONCURRENT_GROUPS):
        #print "spawning %i" % x
        tasks += [gevent.spawn(poolworker, q)]

    q.join()
    gevent.joinall(tasks)

    logging.info("Finished.")

if __name__ == "__main__":
    main()