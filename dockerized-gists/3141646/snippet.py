#!/usr/bin/env python

from pprint import pprint

import boto
import boto.ec2
from boto.ec2.regioninfo import RegionInfo

port=80
access_id = "Your ACCESS_ID"
access_secret = "Your ACCESS_KEY"

regions = boto.ec2.regions(aws_access_key_id=access_id, aws_secret_access_key=access_secret)
print regions
print regions[3].name
print regions[3].endpoint

region_name = "ap-northeast-1"
region_endpoint = "ec2.ap-northeast-1.amazonaws.com"

# first create a region object and connection
region = RegionInfo(name=region_name, endpoint=region_endpoint)

regconn = region.connect(aws_access_key_id=access_id, aws_secret_access_key=access_secret)
groups = regconn.get_all_security_groups()
print groups

# first create a connection to the appropriate host, using your credentials
ec2conn =  boto.connect_ec2(access_id, access_secret, port=port, region=region)

reservations = ec2conn.get_all_instances()
instances = [i for r in reservations for i in r.instances]
for i in instances:
    pprint(i.__dict__)
#    break # remove this to list all instances
