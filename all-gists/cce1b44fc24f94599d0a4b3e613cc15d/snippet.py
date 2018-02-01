#! /usr/bin/python

# This script is taken (unmodified except for this comment) from: https://s3.amazonaws.com/reinvent2013-sec402/SecConfig.py
# Talk: http://www.slideshare.net/AmazonWebServices/intrusion-detection-in-the-cloud-sec402-aws-reinvent-2013

# Example code to output account security config
__author__ = 'Greg Roth'

import boto
import urllib
import hashlib
import argparse

parser = argparse.ArgumentParser(description='outputs security configuration of an AWS account')
parser.add_argument('-a', '--access_key_id', required=True, help='access key id')
parser.add_argument('-k', '--secret_access_key', required=True, help='secret access key')
parser.add_argument('-t', '--security_token', help='security token (for use with temporary security credentials)')
parser.add_argument('-r', '--role', help='role to assume')
parser.add_argument('-v', '--verbose', action="store_true", help='enable verbose mode')
parser.add_argument('-d', '--debug', action="store_true", help='enable debug mode')

args = parser.parse_args()
access_key_id = args.access_key_id
secret_access_key = args.secret_access_key
security_token = args.security_token
sts = boto.connect_sts(access_key_id, secret_access_key)

if args.role:
    assumed_role = sts.assume_role(args.role, "SecAudit")
    access_key_id = assumed_role.credentials.access_key
    secret_access_key = assumed_role.credentials.secret_key
    security_token = assumed_role.credentials.session_token


def debug(str):
    if args.debug:
        print str


def verbose(str):
    if args.verbose or args.debug:
        print str


def sha256(m):
    return hashlib.sha256(m).hexdigest()


def config_line(header, name, detail, data):
    return header + ", " + name + ", " + detail + ", " + data


def config_line_policy(header, name, detail, data):
    verbose("===== " + header + ":  " + name + ":  " + detail + "=====")
    verbose(data)
    verbose("=========================================================")
    return config_line(header, name, detail, sha256(data))


def output_lines(lines):
    lines.sort()
    for line in lines:
        print line


iam = boto.connect_iam(access_key_id, secret_access_key, security_token=security_token)
verbose("Getting account summary:")
summary = iam.get_account_summary()
debug(summary)
output_lines([config_line("iam:accountsummary", "AccountMFAEnabled", "", str(summary["AccountMFAEnabled"]))])

# IAM user info
verbose("Getting IAM user info:")
user_info = []
users = iam.get_all_users().list_users_response.list_users_result.users
debug(users)
for user in users:
    verbose("User: " + user.user_name)
    # User policies
    policies = iam.get_all_user_policies(user.user_name)
    policies = policies.list_user_policies_response.list_user_policies_result.policy_names
    for policy_name in policies:
        policy = iam.get_user_policy(user.user_name, policy_name) \
            .get_user_policy_response.get_user_policy_result.policy_document
        policy = urllib.unquote(policy)
        user_info.append(config_line_policy("iam:userpolicy", user.user_name, policy_name, policy))

    # access keys
    access_keys = iam.get_all_access_keys(user.user_name)
    access_keys = access_keys.list_access_keys_response.list_access_keys_result.access_key_metadata
    for access_key in access_keys:
        user_info.append(
            config_line("iam:accesskey", access_key.user_name, access_key.status, access_key.access_key_id))

    # group membership
    groups = iam.get_groups_for_user(user.user_name)
    groups = groups.list_groups_for_user_response.list_groups_for_user_result.groups
    for group in groups:
        user_info.append(config_line("iam:useringroup", user.user_name, "", group.group_name))
output_lines(user_info)

# IAM groups
verbose("Getting IAM group info:")
group_policy = []
groups = iam.get_all_groups().list_groups_response.list_groups_result.groups
for group in groups:
    verbose("Group " + group.group_name)
    # Policies attached to groups
    policies = iam.get_all_group_policies(group.group_name)
    policies = policies.list_group_policies_response.list_group_policies_result.policy_names
    for policy_name in policies:
        policy = iam.get_group_policy(group.group_name, policy_name)
        policy = policy.get_group_policy_response.get_group_policy_result.policy_document
        policy = urllib.unquote(policy)
        group_policy.append(config_line_policy("iam:grouppolicy", group.group_name, policy_name, policy))

output_lines(group_policy)

# IAM Roles
verbose("Getting IAM role info:")
role_policy = []
roles = iam.list_roles().list_roles_response.list_roles_result.roles
for role in roles:
    verbose("Role: " + role.role_name)
    # Policy controling use of the role (always present)
    assume_role_policy = role.assume_role_policy_document
    assume_role_policy = urllib.unquote(policy)
    role_policy.append(config_line_policy("iam:assumerolepolicy", role.role_name, role.arn, assume_role_policy))


    #Policies around what the assumed role can do
    policies = iam.list_role_policies(role.role_name)
    policies = policies.list_role_policies_response.list_role_policies_result.policy_names
    for policy_name in policies:
        policy = iam.get_role_policy(role.role_name, policy_name)
        policy = policy.get_role_policy_response.get_role_policy_result.policy_document
        policy = urllib.unquote(policy)
        role_policy.append(config_line_policy("iam:rolepolicy", role.role_name, policy_name, policy))
    debug(policies)
output_lines(role_policy)

#  S3 bucket policies
verbose("Getting S3 bucket policies:")
s3 = boto.connect_s3(access_key_id, secret_access_key, security_token=security_token)
bucket_info = []
buckets = s3.get_all_buckets()
for bucket in buckets:
    try:
        policy = bucket.get_policy()
        bucket_info.append(config_line_policy("s3:bucketpolicy", bucket.name, "", policy))
    except boto.exception.S3ResponseError as e:
        bucket_info.append(config_line("s3:bucketpolicy", bucket.name, "", e.code))
output_lines(bucket_info)


# SQS queue policies
verbose("Getting SQS queue policies:")
sqs = boto.connect_sqs(access_key_id, secret_access_key, security_token=security_token)
queue_info = []
queues = sqs.get_all_queues()
for queue in queues:
    try:
        policy = sqs.get_queue_attributes(queue, "Policy")["Policy"]
        queue_info.append(config_line_policy("sqs:queuepolicy", queue.url, "", policy))
    except KeyError:
        queue_info.append(config_line("sqs:queuepolicy", queue.url, "", "NoPolicy"))
output_lines(queue_info)


# SNS topic policies
verbose("Getting SNS topic policies:")
sns = boto.connect_sns(access_key_id, secret_access_key, security_token=security_token)
topic_info = []
topics = sns.get_all_topics()
topics = topics["ListTopicsResponse"]["ListTopicsResult"]["Topics"]
for topic in topics:
    policy = sns.get_topic_attributes(topic["TopicArn"])
    policy = policy["GetTopicAttributesResponse"]["GetTopicAttributesResult"]["Attributes"]["Policy"]
    topic_info.append(config_line_policy("sns:topicpolicy", topic["TopicArn"], "", policy))
output_lines(topic_info)


# EC2 security groups
sg_info = []
ec2 = boto.connect_ec2(access_key_id, secret_access_key, security_token=security_token)
groups = ec2.get_all_security_groups()
for group in groups:
    for rule in group.rules:
        for grant in rule.grants:
            sg_info.append(config_line("ec2:security_group", group.name, str(rule), str(grant)))
output_lines(sg_info)

