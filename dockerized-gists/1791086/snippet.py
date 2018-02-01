import boto

s3 = boto.connect_s3()
bucket = s3.lookup('mybucket')
key = bucket.lookup('mykey')

# Copy the key onto itself, preserving the ACL but changing the content-type
key.copy(key.bucket, key.name, preserve_acl=True, metadata={'Content-Type': 'text/plain'})

key = bucket.lookup('mykey')
print key.content_type