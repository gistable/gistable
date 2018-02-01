#!/usr/bin/env python

#remove public read right for all keys within a directory

#usage: remove_public.py bucketName folderName

import sys
import boto

from boto import connect_s3
from boto.s3 import connect_to_region
from boto.s3.connection import S3Connection, OrdinaryCallingFormat

bucketname = sys.argv[1]
dirname = sys.argv[2]

s3 = connect_to_region(
             'ap-southeast-2',
             aws_access_key_id = 'your_key_here',
             aws_secret_access_key = 'your_secret_here',
             is_secure=True,
             calling_format = OrdinaryCallingFormat()
           )

bucket = s3.get_bucket(bucketname)

keys = bucket.list()

for k in keys:
    new_grants = []
    acl = k.get_acl()
    for g in acl.acl.grants:
        if g.uri != "http://acs.amazonaws.com/groups/global/AllUsers":
            new_grants.append(g)
    acl.acl.grants = new_grants
    k.set_acl(acl)