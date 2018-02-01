#!/usr/bin/env python3
import json

import boto3

def main():
    all_ec2 = {}
    all_rds = {}
    all_cache = {}
    all_elb = {}
    all_redshift = {}
    groups = {}
    defaults = {}
    membership = {}

    region_names = [x['RegionName'] for x in boto3.client('ec2').describe_regions()['Regions']]
    for region_name in region_names:
        print(region_name)

        for sg in boto3.client('ec2', region_name=region_name).describe_security_groups()['SecurityGroups']:
            if sg['GroupName'] == 'default':
                defaults[sg['GroupId']] = region_name
            membership[sg['GroupId']] = []
            groups[sg['GroupId']] = sg

        for reservation in boto3.client('ec2', region_name=region_name).describe_instances()['Reservations']:
            for instance in reservation['Instances']:
                for sg in instance.get('SecurityGroups', []):
                    membership[sg['GroupId']].append(('ec2', instance['InstanceId']))
                all_ec2[instance['InstanceId']] = instance

        for elb in boto3.client('elb', region_name=region_name).describe_load_balancers()['LoadBalancerDescriptions']:
            for sg in elb.get('SecurityGroups', []):
                membership[sg].append(('elb', elb['LoadBalancerName']))
            all_elb[elb['LoadBalancerName']] = elb

        for rds in boto3.client('rds', region_name=region_name).describe_db_clusters()['DBClusters']:
            for sg in rds['VpcSecurityGroups']:
                membership[sg['VpcSecurityGroupId']].append(('rds', rds['DBClusterIdentifier']))
            all_rds[rds['DBClusterIdentifier']] = rds

        try:
            for rs in boto3.client('redshift', region_name=region_name).describe_clusters()['Clusters']:
                for sg in rs['VpcSecurityGroups']:
                    membership[sg['VpcSecurityGroupId']].append(('rs', rs['ClusterIdentifier']))
                all_redshift[rs['lusterIdentifier']] = rs
        except Exception:
            pass

        for cache in boto3.client('elasticache', region_name=region_name).describe_cache_clusters()['CacheClusters']:
            for sg in cache['SecurityGroups']:
                membership[sg['SecurityGroupId']].append(('cache', cache['CacheClusterId']))
            all_cache[cache['CacheClusterId']] = cache

    for x in [membership, groups, defaults, all_ec2, all_elb, all_rds, all_redshift, all_cache]:
        print(json.dumps(x, indent=4, default=lambda x: x.isoformat()))
        print('-' * 80)

    tbd = [x for x in membership if x not in defaults and not membership[x]]
    print('Empty security groups:', ' '.join(tbd))

    tbd = [x for x in defaults if membership[x]]
    print('None empty default groups:', ' '.join(tbd))

if __name__ == '__main__':
    main()