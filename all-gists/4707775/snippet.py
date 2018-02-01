#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written on 2013-02-04 by Philipp Klaus <philipp.l.klaus →AT→ web.de>.
Check <https://gist.github.com/4707775> for newer versions.

Uses dnspython: install with `pip install dnspython3`
"""

import argparse, sys
import urllib.request
import ipaddress
import subprocess
import socket
origGetAddrInfo = socket.getaddrinfo

VERBOSE = False
IPV6_GET = "http://v6.ipv6-test.com/api/myip.php"
IPV4_GET = "http://v4.ipv6-test.com/api/myip.php"

class NoConnectivity(Exception):
    pass

def get_external_IP(get_ipv6=False):
    # replace the original socket.getaddrinfo to force IPv4/IPv6 connection
    # see http://stackoverflow.com/a/6319043/183995
    forced_family = socket.AF_INET6 if get_ipv6 else socket.AF_INET
    def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
        return origGetAddrInfo(host, port, forced_family, socktype, proto, flags)
    socket.getaddrinfo = getAddrInfoWrapper

    try:
        get_addr_url = IPV6_GET if get_ipv6 else IPV4_GET
        retval = urllib.request.urlopen(get_addr_url).read()
        retval = retval.decode('ascii').strip()
    except:
        return None
    try:
        ip = ipaddress.ip_address(retval)
        return retval
    except:
        return None

def get_RR_value(FQDN, kind="A"):
    import dns.resolver
    try:
        answer = dns.resolver.query(FQDN, kind)
        if len(answer) == 0:
            return None
        return answer[0].to_text()
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.NoAnswer:
        return None
    except dns.exception.DNSException:
        return None

def IPs_match_current_RRs(FQDN, want_ipv4=True, want_ipv6=False):
    my_IPv4 = get_external_IP(get_ipv6=False) if want_ipv4 else None
    my_IPv6 = get_external_IP(get_ipv6=True)  if want_ipv6 else None
    if not (my_IPv4 or my_IPv6):
        raise NoConnectivity
    if VERBOSE: print("Current IPv4 and IPv6 addresses:  %s and %s." % (my_IPv4, my_IPv6))
    cur_RR_v4 = get_RR_value(FQDN, 'A')
    cur_RR_v6 = get_RR_value(FQDN, 'AAAA')
    if VERBOSE: print("Current IPv4 and IPv6 RRs in DNS: %s and %s." % (cur_RR_v4, cur_RR_v6))
    return (my_IPv4 == cur_RR_v4 and my_IPv6 == cur_RR_v6)

def update_dns(server, zone, keyfile, domain, ipv4=None, ipv6=None, TTL=30):
    command  = "server %s\n" % server
    command += "zone %s\n" % zone
    command += "update delete %s A\n" % domain
    command += "update delete %s AAAA\n" % domain
    if ipv4:
        command += "update add %s %s    A %s\n" % (domain, TTL, ipv4)
    if ipv6:
        command += "update add %s %s AAAA %s\n" % (domain, TTL, ipv6)
    command += "show\nsend\n"
    command = "nsupdate -k {0} -v << EOF\n{1}\nEOF\n".format(keyfile, command)
    if VERBOSE: print("Calling the following command now:\n\n" + command)
    subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update the RRs of HOSTNAME on a DNS server according to your actual ones.')
    parser.add_argument('--verbose', '-v', action='store_true',
            help='Create more detailed output.')
    parser.add_argument('--ipv6', '-6', action="store_true",
            help='Set IPv4 entry (RR type A).')
    parser.add_argument('--ipv6-getter-url', metavar='URL',
            help='A URL that returns your IPv6 address upon a GET request.')
    parser.add_argument('--ipv4', '-4', action="store_true",
            help='Set IPv6 entry (RR type AAAA).')
    parser.add_argument('--ipv4-getter-url', metavar='URL',
            help='A URL that returns your IPv4 address upon a GET request.')
    parser.add_argument('--zone', '-z', metavar='ZONE',
            help='The zone of the host to update.', required=True)
    parser.add_argument('--keyfile', '-k', metavar='DNSSEC-file.key',
            help='The key file for TSIG.', required=True)
    parser.add_argument('--nameserver', '-n', metavar='NS',
            help='The name server to update.', required=True)
    parser.add_argument('host', metavar='HOSTNAME',
            help='The hostname you want updated.')
    args = parser.parse_args()
    if not (args.ipv4 or args.ipv6): args.ipv4 = True
    if args.ipv6_getter_url:
        IPV6_GET = args.ipv6_getter_url
    if args.ipv4_getter_url:
        IPV4_GET = args.ipv4_getter_url
    if args.verbose: VERBOSE = True

    try:
        match = IPs_match_current_RRs(args.host, want_ipv4=args.ipv4, want_ipv6=args.ipv6)
    except NoConnectivity:
        if VERBOSE: sys.stderr.write("Currently no external IP could be detected. Are you connected in some way?\n")
        sys.exit(1)
    if not match:
        if VERBOSE: print("The current IPs and the RRs do not match. Updating the DNS server...")
        new_ipv4 = get_external_IP(get_ipv6=False) if args.ipv4 else None
        new_ipv6 = get_external_IP(get_ipv6=True)  if args.ipv6 else None
        update_dns(args.nameserver, args.zone, args.keyfile, args.host, ipv4=new_ipv4, ipv6=new_ipv6)
    else:
        if VERBOSE: print("The current IPs and the RRs are matching. Everyting OK.")
    sys.exit(0)

