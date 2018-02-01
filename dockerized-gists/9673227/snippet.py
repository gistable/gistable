#!/usr/bin/env python

"""
ec2-autoscale-instance.py

Read Autoscale DNS from AWS

Sample config file,
{
    "access_key": "key",
    "secret_key": "key",
    "group_name": "groupName"
}
"""

from __future__ import print_function
import argparse
import boto.ec2.autoscale
try:
    import simplejson as json
except ImportError:
    import json

CONFIG_ACCESS_KEY = 'access_key'
CONFIG_SECRET_KEY = 'secret_key'
CONFIG_GROUP_NAME = 'group_name'


def main():
    arg_parser = argparse.ArgumentParser(description=
                                         'Read Autoscale DNS names from AWS')
    arg_parser.add_argument('-c', dest='config_file',
                            help='JSON configuration file containing ' +
                                 'access_key, secret_key, and group_name')
    args = arg_parser.parse_args()
    config = json.loads(open(args.config_file).read())
    access_key = config[CONFIG_ACCESS_KEY]
    secret_key = config[CONFIG_SECRET_KEY]
    group_name = config[CONFIG_GROUP_NAME]

    ec2_conn = boto.connect_ec2(access_key, secret_key)
    as_conn = boto.connect_autoscale(access_key, secret_key)

    try:
        group = as_conn.get_all_groups([group_name])[0]
        instances_ids = [i.instance_id for i in group.instances]
        reservations = ec2_conn.get_all_reservations(instances_ids)
        instances = [i for r in reservations for i in r.instances]
        dns_names = [i.public_dns_name for i in instances]
        print('\n'.join(dns_names))
    finally:
        ec2_conn.close()
        as_conn.close()


if __name__ == '__main__':
    main()