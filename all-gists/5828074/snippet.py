#!/usr/bin/env python
import os
import sys
import argparse

try:
    from boto.ec2.connection import EC2Connection
except ImportError:
    sys.stderr.write('Please install boto ( http://docs.pythonboto.org/en/latest/getting_started.html )\n')
    sys.exit(1)


def get_connection(access_key_id, secret_access_key):
    return EC2Connection(access_key_id, secret_access_key)


def generate_host_map(connection):
    host_map = {}
    for reservation in connection.get_all_instances():
        for instance in reservation.instances:
            host_map[instance.tags.get('Name')] = instance.public_dns_name
    return host_map


def create_ssh_config(connection, default_port=None, default_user=None):
    host_map = generate_host_map(connection)

    host_file = []
    host_file.append('# Add this to your ~/.ssh/config file')

    for host, dns_name in host_map.iteritems():
        host_file.append('Host %s' % (host))
        host_file.append('\tHostName %s' % (dns_name))
        if default_user:
            host_file.append('\tUser %s' % (default_user))
        if default_port:
            host_file.append('\tPort %d' % (default_port))
        host_file.append('')

    return '\n'.join(host_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate an SSH config file with your EC2 hosts inside it'
    )
    parser.add_argument('--access_key_id', '-a',
        help='Your AWS Access Key ID. '
        'Could also be set using the "EC2_ACCESS_KEY_ID" environment variable')
    parser.add_argument('--secret_access_key', '-s',
        help='Your AWS Secret Access Key. Could also '
        'be set using the "EC2_SECRET_ACCESS_KEY" environment variable')
    parser.add_argument('--default_user', '-u',
        help='A default user to append to all hosts')
    parser.add_argument('--default_port', '-p', type=int,
        help='A default port to use when connecting to all hosts')

    args = parser.parse_args()

    if not args.access_key_id:
        args.access_key_id = os.environ.get('EC2_ACCESS_KEY_ID')
    if not args.secret_access_key:
        args.secret_access_key = os.environ.get('EC2_SECRET_ACCESS_KEY')

    if not args.access_key_id or not args.secret_access_key:
        parser.print_help()
        sys.exit(2)

    conn = get_connection(args.access_key_id, args.secret_access_key)
    host_file_content = create_ssh_config(
        conn,
        args.default_port,
        args.default_user
    )
    print(host_file_content)
