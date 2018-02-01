#!/usr/bin/python
import boto
import math

# Use boto to Copy an Object greater than 5 GB Using S3 Multipart Upload API
# probably could be made more pythonesque, based directly off the AWS Java example
# Copy an Object [greater than 5 GB] Using the AWS SDK for Java [S3] Multipart Upload API
# http://docs.aws.amazon.com/AmazonS3/latest/dev/CopyingObjctsUsingLLJavaMPUapi.html

# copy in same bucket as a simple test
bucket_name = 'btest1234'
source_bucket = bucket_name
destination_bucket = bucket_name
orig_key_name = 'foo.gz'
dest_key_name = 'copy' + orig_key_name

s3 = boto.connect_s3(debug=1)
sb = s3.get_bucket(source_bucket)
ky = sb.lookup(orig_key_name)
objectSize = ky.size
print "found objectSize of %d" % objectSize

b = s3.get_bucket(destination_bucket)
mp = b.initiate_multipart_upload(dest_key_name, reduced_redundancy=True)

psize = 50 * math.pow(2.0, 20.0) # 2^20 = 1 MiB

bytePosition = 0
i = 1
while bytePosition < objectSize:
 lastbyte = bytePosition + psize -1
 if lastbyte > objectSize:
   lastbyte = objectSize - 1
 print "mp.copy_part_from_key part %d (%d %d)" % (i,bytePosition,lastbyte)
 mp.copy_part_from_key(source_bucket, orig_key_name, i, int(bytePosition),int(lastbyte))
 i = i+1
 bytePosition += psize

mp.complete_upload()
print "done"