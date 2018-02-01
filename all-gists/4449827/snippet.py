#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Roman Kalyakin
#
# EC2 to Route53 magic
# 
# https://gist.github.com/4449827
#

try:
    from boto import utils, ec2, route53
    from boto.route53.record import ResourceRecordSets
except:
    raise Exception('Boto is not found. $ pip install boto') 

import subprocess

class EC2ToRoute53(object):

    RESOLV_CONF = '/etc/resolvconf/resolv.conf.d/base'
    HOSTNAME_CONF = '/etc/hostname'

    def __init__(self, access_key, secret):
        self.access_key = access_key
        self.secret = secret

    def get_instance_metadata(self, instance_id=None):
        if instance_id is None:
            meta = utils.get_instance_metadata()
            if not meta:
                raise Exception('This machine seems to be not an EC2 instance.')
            instance_id = meta['instance-id']

        ec2_connection = ec2.connection.EC2Connection(self.access_key, self.secret)
        reservations = ec2_connection.get_all_instances([instance_id])
        reservation = reservations[0]
        instance = reservation.instances[0]
        return {
            'instance-id' : instance.id,
            'private-ip' : instance.private_ip_address,
            'public-ip' : instance.ip_address,
            'tags' : instance.tags,
        }

    def add_a_record_to_zone(self, hostname, ip, zone):

        route53_connection = route53.connection.Route53Connection(self.access_key, self.secret)
        zone_id = route53_connection.get_hosted_zone_by_name(zone)
        if not zone_id:
            raise Exception('No such zone found: {}'.format(zone))

        zone_id = zone_id['GetHostedZoneResponse']['HostedZone']['Id'].replace('/hostedzone/','')
        fqdn = '{}.{}'.format(hostname,zone)
        changes = ResourceRecordSets(route53_connection, zone_id)

        # find existing record
        existing_records = route53_connection.get_all_rrsets(zone_id, 'A', fqdn, maxitems=1)
        if existing_records:
            record = existing_records[0]

            if record.resource_records == [ip]:
                print 'Record A {} with {} already exists. Skipping.'.format(fqdn, ip)
                return

            # schedule removal
            print 'Removing existing A record {}'.format(fqdn)
            changes.changes.append(("DELETE", record))

        # add new
        print 'Adding A record {} for {}'.format(fqdn, ip)

        add = changes.add_change('CREATE', fqdn, 'A')
        add.add_value(ip)

        # go for it
        try:
            changes.commit()
            print 'Done.'
        except route53.exception.DNSServerError, e:
            print e.error_message

    def update_hostname_and_search_domains(self, hostname, domains):
        try:
            if domains:
                f = open(self.RESOLV_CONF, 'w')
                f.truncate()
                for domain in domains:
                    f.write("search {}\n".format(domain))
                f.close()
                subprocess.call(['resolvconf', '-u'])
                print 'Updated {}'.format(self.RESOLV_CONF)
        except Exception, e:
            print 'Could not update search domains: {}'.format(e)

        try:
            f = open(self.HOSTNAME_CONF, 'w')
            f.truncate()
            f.write(hostname)
            f.close()
            subprocess.call(['hostname', '-F', self.HOSTNAME_CONF])
            print 'Updated {}'.format(self.HOSTNAME_CONF)
        except Exception, e:
            print 'Could not update hostname: {}'.format(e)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Create a Route53 record from EC2 instance tag value and optinally set hostname and search domains on the server.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-K', '--access-key', required=True, help='AWS Access Key')
    parser.add_argument('-S', '--secret', required=True, help='AWS Secret')
    parser.add_argument('-T', '--tag-name', default='Name', help='EC2 Instance tag name to read hostname from.')
    parser.add_argument('-I', '--instance-id', help='Instance ID. Default to current machine instance ID.')
    parser.add_argument('-P', '--public-zone', help='Zone name to add public IP record to.')
    parser.add_argument('-R', '--private-zone', help='Zone name to add private IP record to.')
    parser.add_argument('-K53', '--access-key-53', help='AWS Access Key for Route53. Defaults to one in -K.')
    parser.add_argument('-S53', '--secret-53', help='AWS Secret for Route53. Defaults to one in -S.')
    parser.add_argument('-U', '--update', action='store_true', default=False, help='Update hostname and search zones.')

    args = parser.parse_args()

    if args.access_key_53 is None or args.secret_53 is None:
        args.access_key_53 = args.access_key
        args.secret_53 = args.secret

    ec2_worker = EC2ToRoute53(args.access_key, args.secret)
    r53_worker = EC2ToRoute53(args.access_key_53, args.secret_53)

    instance_metadata = ec2_worker.get_instance_metadata(args.instance_id)

    if args.tag_name not in instance_metadata['tags']:
        raise Exception('No {} tag for instance.'.format(args.tag_name))

    hostname = instance_metadata['tags'][args.tag_name]

    search_domains = []
    if args.private_zone:
        r53_worker.add_a_record_to_zone(hostname, instance_metadata['private-ip'], args.private_zone)
        search_domains.append(args.private_zone)

    if args.public_zone:
        r53_worker.add_a_record_to_zone(hostname, instance_metadata['public-ip'], args.public_zone)
        search_domains.append(args.public_zone)

    if args.update:
        r53_worker.update_hostname_and_search_domains(hostname, search_domains)
