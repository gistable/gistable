'''
Fabfile for running chef-client across a cluster of servers.

EC2 credentials are automatically read from the knife config file and servers
are discovered via the ec2 API.

Put this file in the root of your chef repo and tehn run ``fab ec2_instances run_chef`` to run "chef-client" on all of your EC2
servers or run ``fab ec2_instances:group_id=web run_chef`` to run
"chef-client" on just the servers in a given security group.

'''

import re

from boto.ec2.connection import EC2Connection
from fabric.api import *

with open('.chef/knife.rb') as knife_config_file:
    knife_config = knife_config_file.read()
    
    results = re.search(r'knife\[\:aws_access_key_id\] *= *[\"\'](?P<access_key>\w+)[\"\']', knife_config)
    EC2_ACCESS_KEY = results.group('access_key')
    results = re.search(r'knife\[\:aws_secret_access_key\] *= *[\"\'](?P<secret_key>.+)[\"\']', knife_config)
    EC2_SECRET_KEY = results.group('secret_key')
    

conn = EC2Connection(EC2_ACCESS_KEY, EC2_SECRET_KEY)

def ec2_instances(group_id=None):
    filters = None
    
    if group_id:
        filters = {'group_id': group_id}
    
    reservations = conn.get_all_instances(filters=filters)
    
    for reservation in reservations:
        instance = reservation.instances[0]
        env.hosts.append(instance.public_dns_name)

def run_chef():
    sudo('chef-client')