#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import re
from datetime import datetime

if len(sys.argv) != 2:
    print "Usage: sslyze_parse.py <sslyze_results.xml>"
    sys.exit()

tree = ET.parse(sys.argv[1])
root = tree.getroot()

sslv2_hosts = []
sslv3_hosts = []
weak_cipher_hosts = []
self_signed_hosts = []
expired_hosts = []
untrusted_ca = []

def printhosts(hostlist):
    hosts = []
    for host in hostlist:
        split_host = re.split('\.|\s\(|\/|\)', host)
        for x in range(0, 5):
            split_host[x] = int(split_host[x])
        hosts.append(split_host)
    sorted_hosts = sorted(hosts)
    for host in sorted_hosts:
        print '.'.join(str(x) for x in host[0:4]), '(' + str(host[4]) + '/' + host[5] + ')'
        #print host
    print

for child in root:
    for target in child:
        ip = target.attrib['ip']
        port = target.attrib['port']
        for finding in target:
            if finding.tag == 'sslv2':
                if not finding.attrib['exception']:
                    entry = ip + " (" + port + "/TCP)"
                    sslv2_hosts.append(entry)
            for detail in finding:
                if detail.tag == 'certificate':
                    try:
                        if detail.attrib['reasonWhyNotTrusted'][:23] == 'self signed certificate':
                            entry = ip + " (" + port + "/TCP)"
                            self_signed_hosts.append(entry)
                        elif detail.attrib['reasonWhyNotTrusted'] == 'unable to get local issuer certificate':
                            entry = ip + " (" + port + "/TCP)"
                            untrusted_ca.append(entry)
                    except:
                        next
                for cipher in detail:
                    if cipher.tag == 'cipherSuite':
                        try:
                            if cipher.attrib['keySize']:
                                bits = cipher.attrib['keySize']
                                bits = bits.split(' ')[0]
                                bits = int(bits)
                                if bits < 128:
                                    entry = ip + " (" + port + "/TCP)"
                                    if entry not in weak_cipher_hosts:
                                        weak_cipher_hosts.append(entry)
                                    next
                        except:
                            next

                    for cert in cipher:
                        if cert.tag == 'notAfter':
                            expiredate = cert.text
                            # remove extra spaces
                            expiredate = ' '.join(expiredate.split())
                            # convert to datetime object
                            expiredate = datetime.strptime(expiredate, '%b %d %H:%M:%S %Y %Z')
                            if expiredate < datetime.today():
                               entry = ip + " (" + port + "/TCP)"
                               if entry not in weak_cipher_hosts:
                                  expired_hosts.append(entry)
                for cipher in detail:
                    if cipher.tag == 'cipherSuite':
                        if detail.tag == 'acceptedCipherSuites':
                            if finding.tag == 'sslv3':
                                entry = ip + " (" + port + "/TCP)"
                                if entry not in sslv3_hosts:
                                   sslv3_hosts.append(entry)

print 'Weak Ciphers Supported:'
printhosts(weak_cipher_hosts)

print 'Self Signed Certificate:'
printhosts(self_signed_hosts)

print 'Expired Certificate:'
printhosts(expired_hosts)

print 'Untrusted CA:'
printhosts(untrusted_ca)

print 'SSLv2 Supported:'
printhosts(sslv2_hosts)

print 'SSLv3 Supported:'
printhosts(sslv3_hosts)