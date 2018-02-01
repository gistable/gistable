#!/usr/bin/env python
# -*- coding: utf-8 -*-

##  OpenVPN Status File Parser by Greg Armer
##  <http://code.geek.sh/2009/07/simple-openvpn-server-statistics/>

STATUS = "/etc/openvpn/openvpn.status"

status_file = open(STATUS, 'r')
stats = status_file.readlines()
status_file.close()

hosts = []

headers = {
    'cn':    'Common Name',
    'virt':  'Virtual Address',
    'real':  'Real Address',
    'sent':  'Sent',
    'recv':  'Received',
    'since': 'Connected Since'
}

sizes = [
    (1<<50L, 'PB'),
    (1<<40L, 'TB'),
    (1<<30L, 'GB'),
    (1<<20L, 'MB'),
    (1<<10L, 'KB'),
    (1,       'B')
]

def byte2str(size):
    for f, suf in sizes:
        if size >= f:
            break

    return "%.2f %s" % (size / float(f), suf)

for line in stats:
    cols = line.split(',')

    if len(cols) == 5 and not line.startswith('Common Name'):
        host  = {}
        host['cn']    = cols[0]
        host['real']  = cols[1].split(':')[0]
        host['recv']  = byte2str(int(cols[2]))
        host['sent']  = byte2str(int(cols[3]))
        host['since'] = cols[4].strip()
        hosts.append(host)

    if len(cols) == 4 and not line.startswith('Virtual Address'):
        for h in hosts:
            if h['cn'] == cols[1]:
                h['virt'] = cols[0]

fmt = "%(cn)-25s %(virt)-18s %(real)-15s %(sent)13s %(recv)13s %(since)25s"
print fmt % headers
print "\n".join([fmt % h for h in hosts])
