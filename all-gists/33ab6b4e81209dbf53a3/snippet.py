#! /usr/bin/env python
# Dyre/Dyreza DGA
# Implementation by Talos
# From http://blogs.cisco.com/security/talos/threat-spotlight-dyre
# Another Python implementation was also posted back in December 2014 by moritz.kroll:
# https://www.virustotal.com/en/file/3716902c64afe40369e6ed67f9b9f7eea30f809348b3558adcff622965e80435/analysis/

from datetime import date
from hashlib import sha256
from socket import gethostbyname, gaierror


def dyre_dga(num, date_str=None):
    if date_str is None:
        date_str = '{0.year}-{0.month}-{0.day}'.format(date.today())

    tlds = ['.cc', '.ws', '.to', '.in', '.hk', '.cn', '.tk', '.so']
    hash = sha256('{0}{1}'.format(date_str, num)).hexdigest()[3:36]
    replace_char = chr(0xFF & ((num % 26) + 97))

    hostname = '{0}{1}{2}'.format(replace_char, hash, tlds[num % len(tlds)])
    try:
        ip = gethostbyname(hostname)
    except gaierror:
        ip = 'not resolving'

    if ip in ['195.22.26.254', '195.22.26.253', '195.22.26.252', '195.22.26.231']:
        ip = 'sinkholed'

    return 'hxxp://{0}:443 ({1})'.format(hostname, ip)


def print_today_domains():
    for i in range(333):
        print(dyre_dga(i))


print_today_domains()