#!/usr/bin/env python3
"""
Renders a partial SSH configuration file from Nodes and Services
located in a specified Consul catalog and then merges other partial
config files into the main ~/.ssh/config file. The Consul based SSH
config follows a convention for the SSH host::

    Host <consul-cluster-name>-<service-name>-<node-address>
        User <ssh-user>
        Hostname <consul-node-address>

For example::

    Host aws-us-east-1-wsgi-app-http-10-0-0-50
        User joe
        Hostname 10.0.0.50

To see available options run::

    consul-ssh-configurator --help
"""


import argparse
import glob
import json
import os
import shutil

from http.client import HTTPConnection


class Client(object):
    def __init__(self, host):
        self.connection = HTTPConnection(host, timeout=10)

    def open(self, method, url, body=None, headers={}):
        self.connection.request(method, url, body, headers)
        response = self.connection.getresponse()
        return json.loads(response.read().decode())

    def get(self, url):
        return self.open('GET', url)


class SshHost(object):

    def __init__(self, host, ssh_user, hostname):
        self.host = host
        self.ssh_user = ssh_user
        self.hostname = hostname


class Inventory(object):

    def __init__(self, ssh_user):
        self.services = {}
        self.ssh_user = ssh_user

    def add_service(self, dc, name, address):
        service = '%s-%s' % (dc, name)
        self.services.setdefault(service, [])
        host = '%s-%s' % (service, address.replace('.', '-'))
        ssh_host = SshHost(host, self.ssh_user, address)
        self.services[service].append(ssh_host)

    def __iter__(self):
        for services in self.services.values():
            for ssh_host in services:
                yield ssh_host


class App(object):

    def __init__(self, consul, ssh_user, merge):
        self.client = Client(consul)
        self.merge = merge
        self.inventory = Inventory(ssh_user)

    def get_datacenters(self):
        return self.client.get('/v1/catalog/datacenters')

    def get_nodes(self, dc=''):
        return self.client.get('/v1/catalog/nodes?dc=%s' % dc)

    def get_node(self, node, dc=''):
        return self.client.get('/v1/catalog/node/%s?dc=%s' % (node['Node'], dc))

    def get_node_services(self, node):
        return [s['Service'] for s in node['Services'].values()]

    def get_inventory(self):
        for dc in self.get_datacenters():
            for node in self.get_nodes(dc):
                node = self.get_node(node, dc)
                for service in self.get_node_services(node):
                    self.inventory.add_service(dc, service, node['Node']['Address'])

    def write_config(self):
        ssh_dir = os.path.join(os.environ['HOME'], '.ssh')
        main_config_path = os.path.join(ssh_dir, 'config')
        main_config_backup_path = os.path.join(ssh_dir, 'config.old')
        consul_config_path = os.path.join(ssh_dir, 'consul.config')
        merge_files = os.path.join(ssh_dir, self.merge)

        with open(consul_config_path, 'w') as f:
            for ssh_host in self.inventory:
                f.write('Host %s\n' % ssh_host.host)
                f.write('  Hostname %s\n' % ssh_host.hostname)
                f.write('  User %s\n\n' % ssh_host.ssh_user)

        shutil.copyfile(main_config_path, main_config_backup_path)
        with open(main_config_path, 'w') as ssh_config:
            for fn in glob.glob(merge_files):
                with open(fn, 'r') as config:
                    ssh_config.write(config.read())
        print('config written to %s' % main_config_path)

    def run(self):
        self.get_inventory()
        self.write_config()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--consul', default='localhost:8500',
        help='The Consul host to connect to. Defaults to localhost:8500')
    parser.add_argument(
        '-u', '--ssh-user', default=os.getlogin(),
        help='The SSH user to specify for all hosts. Defaults to %s' % os.getlogin())
    parser.add_argument(
        '-m', '--merge', default='*.config',
        help='A glob pattern to specify files to collect and merge into the main config. '
             'Defaults to "*.config"')
    args = parser.parse_args()

    App(args.consul, args.ssh_user, args.merge).run()


if __name__ == '__main__':
    main()
