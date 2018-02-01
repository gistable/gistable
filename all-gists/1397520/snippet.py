# A naive dns server with a Redis backend
# Set keys in Redis you want to be authoritative for (set google.com. 127.0.0.1)
# Tip: Use Redis's ttl functions to have temporary names
# Currently only does A records, feel free to fix that
# 
# Licensed under the PSF License
# Thanks to: http://code.activestate.com/recipes/491264-mini-fake-dns-server/
# Author: @Kaerast <alice@kaerast.info>

import socket
import redis # https://github.com/andymccurdy/redis-py

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = None
        
        tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
        if tipo == 0:                     # Standard query
            ini = 12
            lon = ord(data[ini])
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1] + '.'
                ini += lon + 1
                lon = ord(data[ini])
    
    def answer(self, ip):
        packet = []
        if self.domain and ip:
            packet += self.data[:2] + '\x81\x80'
            packet += self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
            packet += self.data[12:]                                         # Original Domain Name Question
            packet += '\xc0\x0c'                                             # Pointer to domain name
            packet += '\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
            packet += ''.join(map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
        if not ip:
            packet += self.data[:2] + '\x81\x80'
            packet += self.data[4:6] + '\x00\x00' + '\x00\x00\x00\x00'   # Questions and Answers Counts
            packet += self.data[12:]                                         # Original Domain Name Question
            packet += '\xc0\x0c'                                             # Pointer to domain name
        return ''.join(packet)

if __name__ == '__main__':
    r = redis.StrictRedis(host='localhost', port=6379, db=0, password='mypassword')
    print 'pyDNS:: dom.query. 60 IN A IP' 
    
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(('',53))
    
    try:
        while True:
            data, addr = udps.recvfrom(1024)
            p = DNSQuery(data)
            ip = r.get(p.domain)
            udps.sendto(p.answer(ip), addr)
            print 'Answer: %s -> %s' % (p.domain, ip)
    except KeyboardInterrupt:
        print 'Finished.'
        udps.close()