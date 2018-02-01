#!/usr/bin/env python

"""
rdns.py

This is a Python script that helps you create
reverse DNS zone files for the Bind Name Server.

I published it together with this blog post: http://goo.gl/CJwly .
"""

import sys

try:
    from ipaddress import IPv6Address, IPv6Network
except ImportError:
    sys.stderr.write("This script needs the ipaddress module from Python3.3+. "
                     "If you run an older version of Python, you should also run an older version of this script.\n")
    sys.exit(2)

#  Monkey patching ipaddress.IPv6Network with a custom method
def combine_with(self, other):
    """
    Function to monkey patch IPv6Network:
    Can combine an IPv6 Network with a host specifier in the form of an IPv6 address.

    n1 = IPv6Network('2003::/64')
    d1 = ipaddress.IPv6Address('::1')
    print(n1.combine_with(d1))
    """
    first = self[0]
    if ((int('1' * self.prefixlen, 2) << (128-self.prefixlen) ) & other._ip) > 0:
        raise ValueError("Cannot combine an IPv6 address with this network. Some bits overlap.")
    return IPv6Address(first._ip | other._ip)
setattr(IPv6Network, 'combine_with', combine_with)

#  Monkey patching ipaddress.IPv6Address with reverse_pointer from Python 3.5+.
def reverse_pointer(self):
    """
    Return the reverse DNS pointer name for the IPv6 address.
    taken from http://hg.python.org/cpython/file/default/Lib/ipaddress.py
    """
    reverse_chars = self.exploded[::-1].replace(':', '')
    return '.'.join(reverse_chars) + '.ip6.arpa'
setattr(IPv6Address, 'reverse_pointer', property(reverse_pointer))


## configure your RDNS generation here:
host = "example.com."
first_name_server = "ns1.example.com."
administrative_contact = "admin.example.com."
subnet = IPv6Network("2001:db8::/32")
rdns_entries = []
# a list of RDNS entries which are of the form (IPv6Address, FQDN)
rdns_entries.append((subnet.combine_with(IPv6Address("::1")), "host1."+host))
rdns_entries.append((subnet.combine_with(IPv6Address("::2")), "host2."+host))

## should not need to modify:
record_ttl = "1h"
from datetime import datetime
zone_serial = datetime.now().strftime("%Y%m%d%H%M%S")
slave_refresh_interval = "1h"
slave_retry_interval = "15m"
slave_expiration_time = "1w"
nxdomain_cache_time = "1h"

### Begin of the output generation

print("; Zone file built with the Python Tool rdns.py:")
print("; " + __doc__.replace("\n","\n; ") )

print("$TTL %s	; Default TTL" % record_ttl )

print("@	IN	SOA	%s	%s (" % (first_name_server, administrative_contact) )
print("	%s	; serial" % zone_serial)
print("	%s	; slave refresh interval" % slave_refresh_interval)
print("	%s	; slave retry interval" % slave_retry_interval)
print("	%s	; slave copy expire time" % slave_expiration_time)
print("	%s	; NXDOMAIN cache time" % nxdomain_cache_time)
print("	)")

print("; domain name servers")
print("@	IN	NS	%s" % first_name_server)

print("; IPv6 PTR entries")
for rdns_entry in rdns_entries:
     print("%s    IN    PTR    %s" % (rdns_entry[0].reverse_pointer, rdns_entry[1]) )
