"""
IAM boto examples:
In this example we create a group that provides access
to all EC2 and S3 resources and actions and then add a
user to that group.
"""
import boto

#
# First create a connection to the IAM service
#
iam = boto.connect_iam()

#
# Now create a group for EC2/S3 users.
# This group will allow members to use all EC2 and S3 functionality
#
ec2s3_policy = """
{
   "Statement":[{
      "Effect":"Allow",
      "Action":["ec2:*", "s3:*"],
      "Resource":"*"
      }
   ]
}"""
response = iam.create_group('EC2-S3-Users')
response = iam.put_group_policy('EC2-S3-Users', 'EC2andS3', ec2s3_policy)

#
# Now create a user and place him in the EC2 group.
#
response = iam.create_user('Bob')
user = response.user
response = iam.add_user_to_group('EC2-S3-Users', 'Bob')

#
# Create AccessKey/SecretKey pair for Bob
#
response = iam.create_access_key('Bob')
access_key = response.access_key_id
secret_key = response.secret_access_key

#
# create connection to EC2 as user Bob
#
ec2 = boto.connect_ec2(access_key, secret_key)

#
# Now do some crazy EC2 shit
#
