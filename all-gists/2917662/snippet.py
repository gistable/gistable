In [1]: policy = """{
   ...:   "Statement":[{
   ...:     "Effect":"Allow",
   ...:     "Action":["s3:*"],
   ...:     "Resource":["arn:aws:s3:::mybucket"]}]}"""
In [2]: import boto
In [4]: c = boto.connect_iam()
In [5]: instance_profile = c.create_instance_profile('myinstanceprofile')
In [6]: role = c.create_role('myrole')
In [7]: c.add_role_to_instance_profile('myinstanceprofile', 'myrole')
Out[7]: {u'add_role_to_instance_profile_response': {u'response_metadata': {u'request_id': u'2221d92c-b437-11e1-86e5-c9c4f3b58653'}}}
In [8]: c.put_role_policy('myrole', 'mypolicy', policy)
Out[8]: {u'put_role_policy_response': {u'response_metadata': {u'request_id': u'2b878c93-b437-11e1-86e5-c9c4f3b58653'}}}
In [9]: c = boto.connect_ec2()
In [10]: c.run_instances('ami-e565ba8c', key_name='mykeyname', security_groups=['mysecuritygroup'], instance_type='t1.micro', instance_profile_name='myinstanceprofile')

