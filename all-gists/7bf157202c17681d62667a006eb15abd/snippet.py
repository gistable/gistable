"""
The most simple DNS client written for Python with asyncio:

* Only A record is support (no CNAME, no AAAA, no MX, etc.)
* Almost no error handling
* Doesn't  support fragmented UDP packets (is it possible?)

"""
import asyncio
import logging
import random
import socket
import struct
import sys

DNS_SERVER = '8.8.8.8'
DNS_PORT = 53
HEADER_LEN = 12

def encode_header(packet_id):
    qr = 0   # is a request (or answer)? (no: request), 1 bit
    opcode = 0 # standard query, 4 bit
    aa = 0   # authorative answer? (no), 1 bit
    tc = 0   # truncated? (no), 1 bit
    rc = 1   # recursive? (yes), 1 bit

    #flags1 = qr | opcode << 1 | aa << 5 | tc << 6 | rc << 7
    flags1 = rc | tc << 1 | aa << 2 | opcode | qr << 7

    ra = 0      # recursivite allowed? (no), 1 bit
    z = 0       # reserved to future use (0), 3 bits
    rcode = 0   # reply type (0: no error), 4 bits

    #flags2 = ra | z << 1 | rcode << 4
    flags2 = rcode | z << 6 | ra << 7

    qdcount = 1  # number of questions
    ancount = 0  # number of replies
    nscount = 0  # number of authorities
    arcount = 0  # number of additionals
    header = struct.pack('!HBBHHHH', packet_id, flags1, flags2, qdcount, ancount, nscount, arcount)
    assert len(header) == HEADER_LEN
    return header

def decode_header(header):
    parts = struct.unpack('!HBBHHHH', header)
    packet_id, flags1, flags2, qdcount, ancount, nscount, arcount = parts

    #flags1 = rc | tc << 1 | aa << 2 | opcode | qr << 7
    #assert qr == 1   # is a request (or answer)? (no: request), 1 bit
    #opcode = 0 # standard query, 4 bit
    #aa = 0   # authorative answer? (no), 1 bit
    #tc = 0   # truncated? (no), 1 bit
    #rc = 1   # recursive? (yes), 1 bit

    # flags2 = rcode | z << 6 | ra << 7
    # ra = 0      # recursivite allowed? (no), 1 bit
    # z = 0       # reserved to future use (0), 3 bits
    # rcode = 0   # reply type (0: no error), 4 bits

    assert nscount == 0  # number of authorities
    assert arcount == 0  # number of additionals
    return (packet_id, qdcount, ancount)

def decode_query(data, offset):
    labels = []
    while True:
        part_len = data[offset]
        offset += 1
        if not part_len:
            break
        label = data[offset:offset+part_len]
        offset += part_len
        labels.append(label)
    # FIXME: support unicode
    labels = [label.decode('utf-8') for label in labels]
    host = '.'.join(labels)

    query_type, query_class = struct.unpack('!HH', data[offset:offset+4])
    offset += 4
    assert query_class == 1
    return host, query_type, offset

def decode_cname(data):
    data_len = data[0]
    subdomain = data[1:1+data_len]
    # FIXME: support unicode
    subdomain = subdomain.decode('utf-8')
    name = data[1+data_len:]
    assert len(name) == 2, repr(name)
    name = struct.unpack('!H', name)
    return (subdomain, name)

def decode_reply(data, offset):
    name, reply_type, reply_class, ttl, data_len = struct.unpack("!HHHIH", data[offset:offset+12])
    offset += 12
    assert reply_class == 1
    reply = data[offset:offset+data_len]
    offset += data_len

    if reply_type == 1:
        reply = socket.inet_ntop(socket.AF_INET, reply)
    elif reply_type == 5:
        reply = decode_cname(reply)

    reply = (name, reply_type, ttl, reply)
    return reply, offset

def encode_query(host):
    # FIXME: support unicode
    parts = [part.encode('ascii') for part in host.split('.')]
    parts.append(b'')
    query = []
    for part in parts:
        query.append(struct.pack('!B', len(part)))
        query.append(part)

    query_type = 1   # A record
    query_class = 1  # IN
    query.append(struct.pack('!HH', query_type, query_class))

    return b''.join(query)

class UdpDnsClientProtocol(asyncio.Protocol):
    def __init__(self):
        self.fut = asyncio.Future()
        self.transport = asyncio.Future()
        self.packet_id = random.randint(0, 2**16-1)

    def connection_made(self, transport):
        self.transport.set_result(transport)

    async def get_transport(self):
        return await self.transport

    async def resolve(self, host):
        # try nice well defined async resolve
        try:
            self.fut = asyncio.Future()
            header = encode_header(self.packet_id)
            query = encode_query(host)
            packet = header + query
            t = await self.get_transport()
            t.sendto(packet)
            ip = await asyncio.wait_for(self.fut, 0.5)
            return ip 
        # fall back to getaddrinfo, and finally 0.0.0.0
        except:
            try:
                res = await loop.getaddrinfo(host, 0)
                return res[-1][-1][0]
            except:
                return '0.0.0.0'


    def datagram_received(self, data, addr):
        result = 'done'
        try:
            (packet_id, qdcount, ancount) = decode_header(data[:HEADER_LEN])
            if packet_id != self.packet_id:
                self.error("invalid packet id")
                return

            offset = HEADER_LEN
            for i in range(qdcount):
                host, query_type, offset = decode_query(data, offset)
                print("QUERY #%s: %r, %s" % (i, host, query_type))
            for i in range(ancount):
                reply, offset = decode_reply(data, offset)
                name, reply_type, ttl, reply = reply
                if reply_type == 1:
                    result = reply
                print("REPLY #%s: %r" % (i, reply))
        except Exception as exc:
            if not self.fut.cancelled():
                self.fut.set_exception(exc)
                return
        if not self.fut.cancelled() and not self.fut.done():
            self.fut.set_result(result)

    def error_received(self, exc):
        print("ERROR RECEIVED", exc)
        self.fut.set_exception(exc)

    # TCP only
    def connection_lost(self, exc):
        if exc:
            print("CONNECTION LOST", exc)
        if not self.fut.done():
            self.fut.set_exception(exc)

async def build_resolver():
    proto = UdpDnsClientProtocol()
    conn = await loop.create_datagram_endpoint(lambda: proto, remote_addr=(DNS_SERVER, DNS_PORT))
    return proto.resolve

if __name__ == "__main__":
    import time
    loop = asyncio.get_event_loop()
    async def test():
        top1m = [x.strip().split(',')[-1] for x in open('top-1m.csv').read().split('\n') if ',' in x]
        resolver = await build_resolver()
        for h in top1m:
            start = time.time()
            res = await resolver(h)
            print(h, res)
            end = time.time()
            print('DUR', end-start)
            sys.stdout.flush()
    #loop.set_debug(True)
    #logging.basicConfig(level=logging.DEBUG)
    loop.run_until_complete(test())
    loop.close()
