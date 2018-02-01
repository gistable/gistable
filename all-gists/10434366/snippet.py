#!/usr/bin/env python
import collections
import datetime
from os import path
import pickle
import sys


if len(sys.argv) < 2:
    print('Usage: bindify.py zonefile')
    sys.exit(0)

# Destination path
PATH = '/etc/bind/'
DOMAIN = sys.argv[1].split('-')[-1]

A = collections.namedtuple('A', ['address', 'hostname'])
CNAME = collections.namedtuple('CNAME', ['alias', 'canonical'])
COMMENT = collections.namedtuple('COMMENT', ['value'])
MX = collections.namedtuple('MX', ['hostname', 'priority', 'mailhost'])
NS = collections.namedtuple('NS', ['hostname'])
PTR = collections.namedtuple('PTR', ['address', 'fqdn'])
TXT = collections.namedtuple('TXT', ['hostname', 'value'])
ZONE = collections.namedtuple('ZONE', ['filename', 'type'])

HEADER = """\
$TTL 3600
@  IN  SOA ns.%s. hostmaster.%s.     (
            %s01           ; serial
            14400                ; refresh
            3600                 ; retry
            1048576              ; expire
            2560                 ; minimum
)

""" % (DOMAIN, DOMAIN, datetime.datetime.now().strftime('%Y%m%d'))

NAMESERVERS = ['ns1.foo.bar', 'ns2.foo.bar']

records = []
ptrs = []

try:
    zones = pickle.loads(open('zones.pickle', 'r').read())
except IOError:
    zones = {}

for nameserver in NAMESERVERS:
    records.append(NS(nameserver))

with open(sys.argv[1], 'r') as handle:
    for line in handle:
        line = line.strip()
        if len(line):
            line = line.replace('\\052', '*')
            parts = line[1:].split(':')
            if line[0:2] in ['#=', '#+', '#C'] or line[0:3] in ['# =', '# +', '# C']:
                #print('Skipping: %s' % line)
                continue
            elif line[0] == '#':
                records.append(COMMENT(line[1:].strip()))
            elif line[0] == '=':
                hostname = '.'.join(parts[0].split('.')[0:-2])
                records.append(A(parts[1], hostname))
                ptrs.append(PTR(parts[1], parts[0]))
            elif line[0] == '+':
                hostname = '.'.join(parts[0].split('.')[0:-2])
                records.append(A(parts[1], hostname))
            elif line[0] == '^':
                ptrs.append(PTR(parts[1], parts[0]))
            elif line[0] == 'C':
                hostname = '.'.join(parts[0].split('.')[0:-2])
                records.append(CNAME(hostname, parts[1]))
            elif line[0] == '@':
                hostname = '.'.join(parts[0].split('.')[0:-2])
                if parts[1]:
                    records.append(A(parts[1], hostname))
                    ptrs.append(PTR(parts[1], parts[0]))
                    records.append(MX(parts[1], parts[3] or 10, parts[0]))
                else:
                    records.append(MX(hostname, parts[1] or 10, parts[0]))
            elif line[0] == "'":
                records.append(TXT(parts[0], parts[1]))
        else:  # Preserve Whitespace
            records.append(None)

# Write out the main zone file
filename = filename = '%s/db.%s' % (PATH, DOMAIN)
with open(filename, 'w') as handle:

    # Dont append zones that already exist
    if DOMAIN not in zones:
        zones[DOMAIN] = ZONE(filename, 'master')

    handle.write(HEADER)

    skip_record = False
    for offset, record in enumerate(records):

        # Preserve Whitespace
        if record is None:
            handle.write('\n')
            continue

        if skip_record:
            skip_record = False
            continue

        record_type = record.__class__.__name__
        if record_type == 'COMMENT':
            handle.write('; %s\n' % record.value)
        elif record_type == 'A':
            # Special case for mailman, yay!
            if len(records) > offset + 1 and records[offset + 1].__class__.__name__ == 'MX':
                handle.write('{0:<45} IN  A     {1}\n'.format(record.hostname, record.address))
                handle.write('{0:<45} IN  MX    {1:<5} {2}.\n'.format(' ', records[offset + 1][1], records[offset + 1][2]))
                skip_record = True
                continue
            handle.write('{0:<45} IN  A     {1}\n'.format(record.hostname, record.address))
        elif record_type == 'CNAME':
            handle.write('{0:<45} IN  CNAME {1}.\n'.format(*record))
        elif record_type == 'MX':
            handle.write('{0:<45} IN  MX    {1:<5} {2}.\n'.format(*record))
        elif record_type == 'NS':
            handle.write('{0:<45} IN  NS    {1}.\n'.format(' ', record[0]))
        elif record_type == 'TXT':
            handle.write('{0:<45} IN  TXT   "{1}"\n'.format(*record))

try:
    ptr_zones = pickle.loads(open('rev-dns-zones.pickle', 'r').read())
except IOError:
    ptr_zones = {}

for record in ptrs:
    octets = record.address.split('.')
    subnet = '.'.join(octets[0:3])
    if subnet not in ptr_zones.keys():
        ptr_zones[subnet] = dict()
    ptr_zones[subnet][int(octets[3])] = record.fqdn

open('rev-dns-zones.pickle', 'w').write(pickle.dumps(ptr_zones))

for zone in ptr_zones:
    rev = zone.split('.')
    rev.reverse()

    name = '%s.in-addr.arpa' % '.'.join(rev)
    filename = '%s/db.%s' % (PATH, zone)

    # Dont append zones that already exist
    if name not in zones:
        zones[name] = ZONE(filename, 'master')

    with open(filename, 'w') as handle:
        handle.write(HEADER)
        for nameserver in NAMESERVERS:
            handle.write('{0:<10} IN  NS    {1}.\n'.format(' ', nameserver))
        handle.write('\n')
        for key in sorted(ptr_zones[zone]):
            handle.write('{0:<10} IN  PTR   {1}.\n'.format(key,
                                                           ptr_zones[zone][key]))



with open('%s/named.conf.local' % PATH, 'w') as handle:
    handle.write("""\
//
// Do any local configuration here
//

""")
    for zone in sorted(zones):
        name = 'zone "%s"' % zone
        filename = path.basename(zones[zone].filename)
        handle.write('{0:<35} {{ type {1}; '
                     'file "/etc/bind/{2}"; }};\n'.format(name,
                                                          zones[zone].type,
                                                          filename))
open('zones.pickle', 'w').write(pickle.dumps(zones))