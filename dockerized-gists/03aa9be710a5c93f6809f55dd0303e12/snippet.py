#!/usr/bin/env python3                                                                                                                                                                                                                        
#  -*- coding: utf-8 -*-                                                                                                                                                                                                                      

import argparse, sys, boto3
from colorama import Fore, Style

def count(my_list, my_key):
    if my_key not in my_list:
        return '0'
    else:
        return str(len(my_list[my_key]))

def append(my_list, my_key, my_value):
    if my_key not in my_list:
        my_list[my_key] = [ my_value ]
    else:
        my_list[my_key].append(my_value)

parser = argparse.ArgumentParser(description='List EC2, RDS and ElastiCache instances, grouped by VPC.')
parser.add_argument('--aws-key', dest='aws_key', help='AWS Key')
parser.add_argument('--aws-secret-key', dest='aws_secret_key', help='AWS Secret Key')
parser.add_argument('--region', dest='region', help='Limit to a single region')
args = parser.parse_args()

if args.aws_key and args.aws_secret_key:
    session = boto3.Session(aws_access_key_id=args.aws_key, aws_secret_access_key=args.aws_secret_key)
else:
    session = boto3.Session()

regions = session.get_available_regions('ec2')

for region in regions:
    print("Region: " + region)
    if (not args.region) or (args.region == region):
        ec2client = session.client('ec2', region)
        rdsclient = session.client('rds', region)
        cacheclient = session.client('elasticache', region)

        instances = {}
        dbs = {}
        caches = {}
        cache_subnets = {}

        ec2_instances = ec2client.describe_instances(Filters=[ { 'Name': 'instance-state-name', 'Values': [ 'running' ] } ])
        for reservation in ec2_instances['Reservations']:
            for instance in reservation['Instances']:
                instance_name = instance['InstanceId']
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = instance['InstanceId'] + ' (' + tag['Value'] + ')'
                append(instances, instance['VpcId'], instance_name)

        db_instances = rdsclient.describe_db_instances()
        for db_instance in db_instances['DBInstances']:
            if 'DBSubnetGroup' in db_instance:
                db_vpc = db_instance['DBSubnetGroup']['VpcId']
                append(dbs, db_vpc, db_instance['DBInstanceIdentifier'])

        aws_cache_subnets = cacheclient.describe_cache_subnet_groups()
        for cache_subnet in aws_cache_subnets['CacheSubnetGroups']:
            cache_subnets[cache_subnet['CacheSubnetGroupName']] = cache_subnet['VpcId']

        cache_clusters = cacheclient.describe_cache_clusters()
        for cache_cluster in cache_clusters['CacheClusters']:
            cache_name = cache_cluster['CacheSubnetGroupName']
            cache_vpc = cache_subnets[cache_name]
            append(caches, cache_vpc, cache_name)

        vpcs = ec2client.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            if vpc['IsDefault'] == False:
                vpc_id = vpc['VpcId']
                for tag in vpc['Tags']:
                    if tag['Key'] == "Name":
                        vpc_name = tag['Value']
                print(Fore.GREEN + Style.BRIGHT + vpc_id + ' | ' + vpc_name + ' | ' + vpc['CidrBlock'] + ' (' + count(instances, vpc_id)  + ' ec2 instances, ' + count(dbs, vpc_id) + ' rds instances, ' + count(caches, vpc_id) + ' elastica\
che instances)' + Style.RESET_ALL)
                if vpc_id in instances:
                    print(Fore.YELLOW + '    ec2 instances: ' + Style.RESET_ALL + ','.join(instances[vpc_id]))
                if vpc_id in dbs:
                    print(Fore.CYAN + '    rds instances: ' + Style.RESET_ALL + ','.join(dbs[vpc_id]))
                if vpc_id in caches:
                    print(Fore.BLUE + '    elasticache instances: ' + Style.RESET_ALL + ','.join(caches[vpc_id]))