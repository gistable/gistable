#!/usr/bin/env python
# encoding: utf-8
"""
portforwarder.py

Created by Sandro Gauci on 2014-03-18.
"""

import sys
import os
import asyncio
import argparse

# starts the connection with the real server
class ForwardedConnection(asyncio.Protocol):
    
    def __init__(self, peer):
        self.peer = peer
        self.transport = None
        self.buff = list()
    
    # when a connection is made, we check if there's anything that was sent 
    # previously and stored in a buffer, and we send it immediately
    def connection_made(self, transport):
        self.transport = transport
        if len(self.buff) > 0:
            self.transport.writelines(self.buff)
            self.buff = list()
    
    def data_received(self,data):
        self.peer.write(data)
    
    def connection_lost(self, exc):
        self.peer.close()

# an instance of PortForwarder will be created for each client connection.
class PortForwarder(asyncio.Protocol):
    def __init__(self, dsthost, dstport):
        self.dsthost = dsthost 
        self.dstport = dstport
        
    def connection_made(self, transport):
        self.transport = transport
        loop = asyncio.get_event_loop()
        self.fcon = ForwardedConnection(self.transport)
        asyncio.async(loop.create_connection(lambda: self.fcon, self.dsthost, self.dstport))
        

    def data_received(self, data):
        if self.fcon.transport is None:
            self.fcon.buff.append(data)
        else:            
            self.fcon.transport.write(data)

    def connection_lost(self, exc):
        self.fcon.transport.close()

def getargs():
    parser = argparse.ArgumentParser(description="forward a local port to a remote host")
    parser.add_argument('-p','--port',type=int,help="destination port",default=80)
    parser.add_argument('host',help="destination host")
    parser.add_argument('-P','--localport',type=int,help="listen on local port", default=4444)
    return(parser.parse_args())

def main():
    args = getargs()
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(loop.create_server(lambda: PortForwarder(args.host,args.port), '127.0.0.1', args.localport))
    try:
        loop.run_until_complete(server.wait_closed())
    except KeyboardInterrupt:
        sys.stderr.flush()
        print('\nStopped\n')

if __name__ == '__main__':
    main()



