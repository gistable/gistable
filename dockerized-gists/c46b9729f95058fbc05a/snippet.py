#!/usr/bin/env python
# http://blog.vrypan.net/2012/12/20/dynamic-dns-with-route53/
from area53 import route53
from boto.route53.exception import DNSServerError
import subprocess
import sys

def get_ip():
    p = subprocess.Popen("/usr/bin/dig +short @resolver1.opendns.com myip.opendns.com", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()

    if not err:
        return output.strip();
    else:
        sys.exit(1)

def main():
    sub_domain = 'home'
    domain = 'tylercipriani.com'
    fqdn = '%s.%s' % (sub_domain, domain)

    zone = route53.get_zone(domain)
    a_rec = zone.get_a(fqdn)
    new_ip = get_ip()

    if (a_rec):
        if new_ip == a_rec.resource_records[0]:
            print '%s is current. (%s)' % (fqdn, new_ip)
            sys.exit(0)

        try:
            zone.update_a(fqdn, new_ip, 900)
        except DNSServerError:
            zone.add_a(fqdn, new_ip, 900)

    else:
        zone.add_a(fqdn, new_ip, 900)

if __name__ == '__main__':
    main()