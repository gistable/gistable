# Find the IAM username belonging to the TARGET_ACCESS_KEY
# Useful for finding IAM user corresponding to a compromised AWS credential

# Requirements:
#
# Environmental variables: 
# 		AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# python: 
#		boto

import boto.iam

TARGET_ACCESS_KEY = 'TARGET_KEY'

iam = boto.connect_iam()

users = iam.get_all_users('/')['list_users_response']['list_users_result']['users']

def find_key():
	for user in users:
		for key_result in iam.get_all_access_keys(user['user_name'])['list_access_keys_response']['list_access_keys_result']['access_key_metadata']:
			aws_access_key = key_result['access_key_id']
			if aws_access_key == TARGET_ACCESS_KEY:
				print 'Target key belongs to:'
				print 'user : ' + user['user_name']
				return True
	return False

if not find_key():
	print 'Did not find access key (' + TARGET_ACCESS_KEY + ') in ' + str(len(users)) + ' IAM users.'