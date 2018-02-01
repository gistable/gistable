#!/usr/bin/python
# This script will query a name server nonrecursively
# RFC 1912 recommends that the $TTL value on the name server 
# be set to 1 day or longer
# -*- coding: utf-8 -*-

import sys
import dns  
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *
from dns.message import *
from dns.query import *

if len(sys.argv) == 3:
    script, malwareFile, nameServer = sys.argv
else:
    print '''
    This script needs three arguments
    Usage: python dnsNonRcv.py malwarefile nameserverIP
            '''
    sys.exit (1)

malwareFile = sys.argv[1]
nameserver = sys.argv[2]
domainFile = open(malwareFile)

for line in domainFile.readlines():
    domain = line.split()[0]
    response = None
            # create the query
    query = dns.message.make_query(domain, dns.rdatatype.A, dns.rdataclass.IN)
            # unset the recurse flag 
    query.flags ^= dns.flags.RD

    try:
        response = dns.query.udp(query, nameserver)
    except DNSException:
        response = []
    if response.rcode() == dns.rcode.REFUSED:  #
        print '''
        The name server answered, but refuses to 
        perform the specified operation. 
        Contact your DNS administrator.
        ''' # This can be for any policy reason
            # including because we unset the recurse flag.
        sys.exit (1)
    if len(response.answer) > 0:
        print '%s  ======> Found Record!' % domain
    else:
        print '%s [*] No Record.' % domain
    continue