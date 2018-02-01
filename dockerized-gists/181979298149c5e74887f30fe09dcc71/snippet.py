#!/usr/bin/env python3

# How to use:
#
# LE_HOSTED_ZONE=XXXXXX LE_AWS_PROFILE=dns-access ./letsencrypt.sh --cron --domain example.org --challenge dns-01 --hook /tmp/hook-dns-01-lets-encrypt-route53.py
#
# More info about letsencrypt.sh: https://github.com/lukas2511/letsencrypt.sh/wiki/Examples-for-DNS-01-hooks
# Using AWS Profiles: http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-multiple-profiles
# Obtaining your Hosted Zone ID from Route 53: http://docs.aws.amazon.com/cli/latest/reference/route53/list-hosted-zones-by-name.html

# modules declaration
import os
import sys
import boto3
from time import sleep

if 'LE_HOSTED_ZONE' not in os.environ:
    raise Exception("Environment variable LE_HOSTED_ZONE not defined")

if 'LE_AWS_PROFILE' not in os.environ:
    raise Exception("Environment variable LE_AWS_PROFILE not defined")

# declaring variables
aws_profile = os.environ['LE_AWS_PROFILE']
hosted_zone_id = os.environ['LE_HOSTED_ZONE']

def setup_dns(domain, txt_challenge):
    global aws_profile
    global hosted_zone_id

    session = boto3.Session(profile_name=aws_profile)
    client = session.client("route53")

    resp = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': '_acme-challenge.{0}'.format(domain),
                    'Type': 'TXT',
                    'TTL': 60,
                    'ResourceRecords': [{
                        'Value': '"{0}"'.format(txt_challenge)
                    }]
                }
            }]
        }
    )

    # wait 30 seconds for DNS update
    sleep(30)

def delete_dns(domain, txt_challenge):
    global aws_profile
    global hosted_zone_id

    session = boto3.Session(profile_name=aws_profile)
    client = session.client("route53")

    resp = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': '_acme-challenge.{0}'.format(domain),
                    'Type': 'TXT',
                    'TTL': 60,
                    'ResourceRecords': [{
                        'Value': '"{0}"'.format(txt_challenge)
                    }]
                }
            }]
        }
    )

if __name__ == "__main__":
    hook = sys.argv[1]
    domain = sys.argv[2]
    txt_challenge = sys.argv[4]

    print(hook)
    print(domain)
    print(txt_challenge)

    if hook == "deploy_challenge":
        setup_dns(domain, txt_challenge)
    elif hook == "clean_challenge":
        delete_dns(domain, txt_challenge)
