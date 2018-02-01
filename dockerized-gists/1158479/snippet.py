#!/bin/env python

"""
This is a test script to simulate a memcached instance on a server
that has gone south and is accepting connections, but generally not
responding. 

The goal of this script is to help test/develop correct client 
side settings for timeouts/failure scenarios

by Jehiah Czebotar <jehiah@gmail.com> http://jehiah.cz/
"""

import socket
import time

MEMCACHED_PORT=11211
LISTEN_BACKLOG=1024
SLEEP_LOOP=10
MAX_CONNECTIONS=25

def simulate_memcached():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', MEMCACHED_PORT))
    s.listen(LISTEN_BACKLOG)

    connections = []
    i = 0
    while True:
        i+=1
        conn, addr = s.accept()
        print i, conn, addr
        connections.append(conn)
        while len(connections) > MAX_CONNECTIONS:
            conn = connections.pop(0)
            time.sleep(SLEEP_LOOP)
            print "closing", conn
            conn.close()

if __name__ == "__main__":
    simulate_memcached()
