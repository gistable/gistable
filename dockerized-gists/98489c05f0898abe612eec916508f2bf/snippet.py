#!/usr/bin/env python

# How to use:
#
# Ubuntu 16.04: apt install -y python-boto OR apt install -y python3-boto
#
# Specify the default profile on aws/boto profile files or use the optional AWS_PROFILE env var:
# AWS_PROFILE=example ./dehydrated -c -d example.com -t dns-01 -k /etc/dehydrated/hooks/route53.py
#
# Manually specify hosted zone:
# HOSTED_ZONE=example.com AWS_PROFILE=example ./dehydrated -c -d example.com -t dns-01 -k /etc/dehydrated/hooks/route53.py
#
# More info about dehaydrated and dns challenge: https://github.com/lukas2511/dehydrated/wiki/Examples-for-DNS-01-hooks
# Using AWS Profiles: http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-multiple-profiles

import os
import sys
from boto.route53 import *
from time import sleep


def route53_dns(domain, txt_challenge, action='upsert'):

    conn = connection.Route53Connection()

    if 'HOSTED_ZONE' in os.environ:
      hosted_zone = os.environ['HOSTED_ZONE']
      if not domain.endswith(hosted_zone):
        raise Exception("Incorrect hosted zone for domain {0}".format(domain))
      zone = conn.get_hosted_zone_by_name("{0}.".format(hosted_zone))
      zone_id = zone['GetHostedZoneResponse']['HostedZone']['Id'].replace('/hostedzone/', '')
    else:
      zones = conn.get_all_hosted_zones()
      for zone in zones['ListHostedZonesResponse']['HostedZones']:
        if "{0}.".format(domain).endswith(zone['Name']):
          zone_id = zone['Id'].replace('/hostedzone/', '')
          break
      else:
        raise Exception("Hosted zone not found for domain {0}".format(domain))

    change_set = record.ResourceRecordSets(conn, zone_id)
    change = change_set.add_change("{0}".format(action.upper()), '_acme-challenge.{0}'.format(domain), type='TXT', ttl=60)
    change.add_value('"{0}"'.format(txt_challenge))
    change_set.commit()

    if action.upper() == 'UPSERT':
      # wait for DNS update
      sleep(30)

if __name__ == "__main__":
    hook = sys.argv[1]
    if len(sys.argv) > 2:
        domain = sys.argv[2]
        txt_challenge = sys.argv[4]
    else:
        domain = None
        txt_challenge = None

    print("hook: {0}".format(hook))
    print("domain: {0}".format(domain))
    print("txt_challenge: {0}".format(txt_challenge))

    if hook == "deploy_challenge":
        route53_dns(domain, txt_challenge, 'upsert')
    elif hook == "clean_challenge":
        route53_dns(domain, txt_challenge, 'delete')