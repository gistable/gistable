#!/usr/bin/env python
import os
import argparse
import yaml


class IRosterFactory(object):

    """ Interface for objects that can generate a Salt roster """

    def __init__(self, args):
        self.args = args

    @staticmethod
    def add_arguments(parser):
        """ Add any provider-specific args to the parser """
        raise NotImplementedError

    def get_hosts(self):
        """ Get a mapping of server names to ip addresses """
        raise NotImplementedError


class DORosterFactory(IRosterFactory):

    """ Roster factory for droplets on Digital Ocean """

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--client-id', help="Digital Ocean client id")
        parser.add_argument('--api-key', help="Digital Ocean api key")
        parser.add_argument('--do-private', action='store_true',
                            help="Use private ip addresses")

    def get_hosts(self):
        import requests
        params = {
            'client_id': self.args.client_id,
            'api_key': self.args.api_key,
        }
        response = requests.get('https://api.digitalocean.com/droplets/',
                                params=params)
        droplets = response.json()['droplets']
        hosts = {}
        for droplet in droplets:
            if not self.args.do_private:
                hosts[droplet['name']] = droplet['ip_address']
            elif droplet['private_ip_address'] is not None:
                hosts[droplet['name']] = droplet['private_ip_address']
        return hosts


class AWSRosterFactory(IRosterFactory):

    """ Roster factory for EC2 servers on AWS """

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--region', default='us-west-1',
                            help="The AWS region to use (default %(default)s)")
        parser.add_argument('--access-key-id',
                            default=os.environ.get('AWS_ACCESS_KEY_ID'),
                            help="Your AWS access key id. Defaults to the "
                            "environment variable AWS_ACCESS_KEY_ID.")
        parser.add_argument('--secret-access-key',
                            default=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                            help="Your AWS secret. Defaults to the environment "
                            "variable AWS_SECRET_ACCESS_KEY.")
        parser.add_argument('--aws-private', action='store_true',
                            help="Use private ip addresses")

    def get_hosts(self):
        import boto.ec2
        conn = boto.ec2.connect_to_region(
            self.args.region,
            aws_access_key_id=self.args.access_key_id,
            aws_secret_access_key=self.args.secret_access_key)
        id_map = {}
        servers = {}
        tags = conn.get_all_tags()
        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                id_map[instance.id] = instance
        for tag in tags:
            try:
                if tag.name.lower() == "name":
                    instance = id_map[tag.res_id]
                    if self.args.aws_private:
                        servers[tag.value] = instance.private_ip_address
                    else:
                        servers[tag.value] = instance.ip_address
            except KeyError:
                pass
        return servers


__all_factories__ = {
    'aws': AWSRosterFactory,
    'digitalocean': DORosterFactory,
}


def main():
    """ Generate a salt roster from your cloud servers """
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument('cloud', choices=__all_factories__.keys(),
                        help="The cloud provider")
    parser.add_argument('-o', '--outfile', default='/etc/salt/roster',
                        help="Write this roster to this file (default "
                        "%(default)s)")
    parser.add_argument('-u', '--user', default='ubuntu',
                        help="The user account for ssh login "
                        "(default %(default)s)")
    parser.add_argument('-n', '--no-sudo', action='store_true',
                        help="Do not use sudo on the remote servers")

    for name, reader in __all_factories__.iteritems():
        group = parser.add_argument_group(name, reader.__doc__)
        reader.add_arguments(group)

    args = parser.parse_args()
    factory_class = __all_factories__[args.cloud]
    factory = factory_class(args)
    hosts = factory.get_hosts()
    roster = {}
    for name, ip in hosts.iteritems():
        roster[name] = {
            'host': ip,
            'user': args.user,
            'sudo': not args.no_sudo,
        }
    with open(args.outfile, 'w') as ofile:
        yaml.safe_dump(roster, ofile)

if __name__ == '__main__':
    main()