#!/usr/bin/env python

from __future__ import print_function
import argparse
import json
import chef
import os
import sys
import re
from time import time
import ConfigParser

try:
    import json
except ImportError:
    import simplejson as json

class ChefInventory:
    def __init__(self):
        self.parser = self._create_parser()
        self.chef_server_url = ""
        self.client_key = ""
        self.client_name = ""
        self.cache_max_age = 3600
        self.cache_path =  os.path.join(os.path.expanduser('~'),'.ansible-chef.cache')

        self.read_settings()

        if self.chef_server_url and self.client_key and self.client_name:
            print("Using chef ini values", file=sys.stderr)
            self.api = chef.ChefAPI(self.chef_server_url, self.client_key, self.client_name)
        else:
            print("Trying chef autoconfiguration", file=sys.stderr)
            self.api=chef.autoconfigure()
        if not self.api:
            print("Could not find chef configuration", file=sys.stderr)
            sys.exit(1)

    def read_settings(self):
        config = ConfigParser.SafeConfigParser()
        chef_default_ini_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'chef.ini')
        chef_ini_path = os.environ.get('CHEF_INI_PATH', chef_default_ini_path)
        config.read(chef_ini_path)

        if config.has_option('chef', 'cache_path'):
            cache_dir = os.path.expanduser(config.get('chef', 'cache_path'))
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            self.cache_path = cache_dir + "/ansible-chef.cache"

        if config.has_option('chef', 'cache_max_age'):
            self.cache_max_age = int(config.get('chef', 'cache_max_age'))
        if config.has_option('chef', 'chef_server_url'):
            self.chef_server_url = config.get('chef', 'chef_server_url')
        if config.has_option('chef', 'client_key'):
            self.client_key = config.get('chef', 'client_key')
        if config.has_option('chef', 'client_name'):
            self.client_name = config.get('chef', 'client_name')


    def refresh_cache(self):
        print("REFRESHING CACHE - COULD TAKE A WHILE", file=sys.stderr)
        with self.api:
            data = {}
            nodes = chef.Search("node")
            for n in nodes:
                data[n["name"]] = n
            self.write_cache(data)

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description=u'Chef Server Dynamic Inventory for Ansible.'
        )
        parser.add_argument(u'--list', action=u'store_true',
                            help=u'List all nodes.')
        parser.add_argument(u'--host', help=u'Retrieve variable information.')
        parser.add_argument(u'--refresh-cache',  action=u'store_true', help=u'Refresh the cache')
        return parser
  
    def read_cache(self):
        cache = open(self.cache_path, 'r')
        data = json.loads(cache.read())
        return data

    def write_cache(self, data):
        json_data = self.json_format_dict(data, True)
        cache = open(self.cache_path, 'w')
        cache.write(json_data)
        cache.close()
   
    def is_cache_valid(self):
       if os.path.isfile(self.cache_path):
            mod_time = os.path.getmtime(self.cache_path)
            current_time = time()
            if (mod_time + self.cache_max_age) > current_time:
                return True
       return False

    def json_format_dict(self, data, pretty=False):
        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
        else:
            return json.dumps(data)

    def to_safe(self, word):
        return re.sub("[^A-Za-z0-9\-]", "_", word)

    def list_nodes(self):
        groups = {}
        meta = { "_meta" : { "hostvars" : {} } } 
        groups.update(meta)

        data = self.read_cache()
        for name, node in data.iteritems():
            # make sure node is configured/working
            if ( "ipaddress" in node["automatic"].keys() ):
                ip=node["automatic"]["ipaddress"] 
            else:
                continue
       
            # create a list of environments
            environment = self.to_safe(node["chef_environment"])
            if environment not in groups:
                groups[environment] = []
            groups[environment].append(ip)

            for r in node["automatic"]["roles"]:
                role = self.to_safe(r)
                if role not in groups:
                    groups[role] = []
                groups[role].append(ip)

            for i in node["run_list"]:
                m = re.match(r'(role|recipe)\[(.*)\]', i)
                item = self.to_safe(m.group(2))
                if item not in groups:
                    groups[item] = []
                groups[item].append(ip)

        print(self.json_format_dict(groups, pretty=True))


    def node_variables(self):
        print(json.dumps(dict()))

    def execute(self):
        args = self.parser.parse_args()
        if args.refresh_cache:
            self.refresh_cache()
        elif not self.is_cache_valid():
            self.refresh_cache()
        if args.list:
            self.list_nodes()
        else:
            self.node_variables()

def main():
    ci = ChefInventory()
    ci.execute()


if __name__ == '__main__':
    main()
