#!/usr/bin/env python

import sys
import gevent
from gevent import Greenlet
from gevent.pool import Pool
from gevent.server import StreamServer
from gevent.socket import create_connection

bind_addr = '127.0.0.1'
port = 32392

clients = int(sys.argv[1])
successful_clients = 0
client_count = 0
server_count = 0

def server_conn(sock, addr):
    global server_count
    server_count += 1
    
    f = sock.makefile()
    line = f.readline()
    while line:
        gevent.sleep(0.1)
        f.write(line)
        f.flush()
        line = f.readline() 

def start_server():
    pool   = Pool(5000)
    server = StreamServer((bind_addr, port),
                          server_conn,
                          spawn=pool)
    server.serve_forever()

def start_client():
    global successful_clients, client_count
    client_count += 1

    line = "hi there\n"
    s = create_connection((bind_addr, port))
    f = s.makefile()
    f.write(line)
    f.flush()
    gevent.sleep(0)
    assert line == f.readline()
    s.close()
    successful_clients += 1

Greenlet.spawn(lambda: start_server())
gl = []
for i in range(clients):
    gl.append(Greenlet.spawn(lambda: start_client()))
for g in gl:
    g.join()

print "total clients: %d" % clients
print "   successful: %d" % successful_clients
print "  client conn: %d" % client_count
print "  server conn: %d" % server_count
