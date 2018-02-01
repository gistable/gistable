#!/usr/bin/env python
#
# Query the Steam master servers.
#
# See: http://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol
#
# Koen Bollen <meneer koenbollen nl>
# 2010 GPL
#

import socket

# Master server:
GOLD_SRC = ( "hl1master.steampowered.com", 27010 )
SOURCE = ( "hl2master.steampowered.com", 27011 )

# Regions:
US_EAST_COAST = 0x00
US_WEST_COAST = 0x01
SOUTH_AMERICA = 0x02
EUROPE        = 0x03
ASIA          = 0x04
AUSTRALIA     = 0x05
MIDDLE_EAST   = 0x06
AFRICA        = 0x07
ALL           = 0xFF

def _buildpacket( first, region, filters ):
    first = "%s:%d" % first
    filters = "".join( ["\\%s\\%s"%pair for pair in filters.items()] )
    return "1%c%s\0%s\0" % ( region, first, filters )

def _parse( data ):
    if data[:6] != "\xff\xff\xff\xfff\n":
        return
    data = data[6:]
    while data:
        ip = socket.inet_ntoa( data[:4] )
        port = ord(data[4:5])<<8 | ord(data[5:6])
        yield ip, port
        data = data[6:]

def query( master=SOURCE, region=ALL, **filters ):
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.connect( master )
    first = last = ( "0.0.0.0", 0 )
    while True:
        sock.sendall( _buildpacket( last, region, filters ) )
        data = sock.recv(4096)
        for server in _parse( data ):
            last = server
            if last != first:
                yield server
        if last == first:
            break

if __name__ == "__main__":

    print "Listing Team Fortress servers asynchronous..."
    for server in query(gamedir='tf'):
        print server
    print "done"
    print

    print "Fetching Europe's Counter-Strike servers playing de_dust2..."
    cstrike = set( query( region=EUROPE, gamedir="cstrike", map="de_dust2" ) )
    print "done, length =", len( cstrike )

    if len( set( query( gamedir="yourmom" ) ) ) > 0:
        print "Wait... what?!"

# vim: expandtab
