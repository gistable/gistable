from dns.resolver import Resolver, query, NXDOMAIN
import dns.query
from dns.exception import Timeout
from dns.message import make_query
from dns.rdatatype import NS
import socket
from random import choice

def get_zone_nameservers(zone):
    nss = []
    for answer in query(zone, 'NS'):
        nss.append(socket.gethostbyname(answer.to_text()))
    return nss

def names_to_nameservers(names):
    zone_nss = {}
    for name in names:
        domain, zone = name.split('.', 1)
        if zone not in zone_nss:
            zone_nss[zone] = get_zone_nameservers(zone + '.')
        msg = make_query(name + '.', NS)
        ns = choice(zone_nss[zone])
        response = dns.query.udp(msg, ns)
        yield (name, tuple(sorted(rr.target.to_text() for rr in response.authority[0] if rr.rdtype == NS)))
 
with open('domains.txt', 'r') as fh:
    for host, nss in names_to_nameservers(line.rstrip() for line in fh):
        if nss == ():
            ns = "NONE"
        else:
            ns = "\n\t".join(nss)
        print host + "\n\t" + ns + "\n"