#!/usr/bin/env python

# Compare a file on S3 to see if we have the latest version
# If not, upload it and invalidate CloudFront

import fnmatch
import os
import boto
import pprint
import re
import hashlib
from boto.s3.key import Key

# Where source is checked out
SOURCE_DIR  = '/local/path/to/source/code'
BUCKET_NAME = 'my-s3-bucket-name'

# Connect to S3 and get bucket
conn = boto.connect_s3()
bucket = conn.get_bucket(BUCKET_NAME)

# Shortcut to MD5
def get_md5(filename):
  f = open(filename, 'rb')
  m = hashlib.md5()
  while True:
    data = f.read(10240)
    if len(data) == 0:
        break
    m.update(data)
  return m.hexdigest()

def to_uri(filename):
  return re.sub(SOURCE_DIR, '', f)

# Assemble a list of all files from SOURCE_DIR
files = []
for root, dirnames, filenames in os.walk(SOURCE_DIR):
  for filename in filenames:
    files.append(os.path.join(root, filename))

# Compare them to S3 checksums
files_to_upload = []
for f in files:
  uri = to_uri(f)
  key = bucket.get_key(uri)
  if key is None:
    # new file, upload
    files_to_upload.append(f)
  else:
    # check MD5
    md5  = get_md5(f)
    etag = key.etag.strip('"').strip("'")
    if etag != md5:
      print(f + ": " + md5 + " != " + etag)
      files_to_upload.append(f)
            
# Upload + invalidate the ones that are different
for f in files_to_upload:
  uri = to_uri(f)
  key = Key(bucket)
  key.key = uri
  key.set_contents_from_filename(f)
  # CloudFront invalidation code goes here


