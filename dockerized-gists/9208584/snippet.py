#!/usr/bin/python
from os import environ
from socket import gethostname

from boto import connect_route53
from boto.route53.record import ResourceRecordSets

IF_NAME = 'ppp0'
AWS_ACCESS_KEY = '...'
AWS_SECRET_KEY = '...'
ZONE_ID = 'ZQ...'

def main():
    currentInterface = environ.get('PPP_IFACE')
    if currentInterface:
        if currentInterface != IF_NAME:
            return
        address = environ.get('PPP_LOCAL')
    if not address:
        return
    hostname = gethostname()

    conn = connect_route53(AWS_ACCESS_KEY, AWS_SECRET_KEY)
    rrset = conn.get_all_rrsets(ZONE_ID, 'A', hostname, maxitems=1)[0]
    if address not in rrset.resource_records:
        changes = ResourceRecordSets(conn, ZONE_ID)
        change1 = changes.add_change('DELETE', hostname, 'A', rrset.ttl)
        for rr in rrset.resource_records:
            change1.add_value(rr)
        change2 = changes.add_change('CREATE', hostname, 'A', rrset.ttl)
        change2.add_value(address)
        changes.commit()


if __name__ == '__main__':
    main()
