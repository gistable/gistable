#!/usr/bin/python

"""

S3 to Rackspace Cloud Files Migration

This script will copy the contents of a S3
bucket to to a Rackspace Cloud Files container.

Depends on the boto and python_cloudfiles python libraries.

Author:		Tony Landis 
Website:	www.tonylandis.com
License:	Do whatever you want with this code
Usage:		Just define the S3_* and CF_* settings below before running.
			If you have a s3 bucket name with characters that are not
			valid for a file name on your system, you will need to change
			the tmp_file and mrk_file as well to avoid issues.


"""

import cloudfiles
from boto.s3.connection import S3Connection
from boto.s3.key import Key

# the s3 api key, secret, and bucket to copy from
S3_KEY			= ''
S3_SECRET		= ''
S3_BUCKET		= ''

# the rackspakce cloud files user, api, and container to copy to
CF_USER			= ''
CF_API_KEY		= ''
CF_CONTAINER	= ''

# connect to s3
s3_conn			= S3Connection(S3_KEY, S3_SECRET, is_secure=False)
s3_bucket		= s3_conn.create_bucket(S3_BUCKET)
# connect to cf
cf_conn			= cloudfiles.get_connection(CF_USER, CF_API_KEY, serviceNet=True)
cf_container	= cf_conn.get_container(CF_CONTAINER)
# setup temp files
tmp_file = '/tmp/%s' % S3_BUCKET
mrk_file = '/tmp/key_%s' % S3_BUCKET
#see if we have a file with the key marker for s3 get_all_keys()
key_marker=''
try:
	fp = open(mrk_file, 'r')
	lines = fp.readlines()
	fp.close()
	if lines:
		key_marker = lines[-1]
except Exception: 
	pass

def handle(name):
	"try to do the copy"
	try:
		#get tmp file
		key = Key(s3_bucket, name)
		#copy to tmp
		fp = open(tmp_file, "w")
		key.get_file(fp)
		fp.close()
		#copy to cf
		fp = open(tmp_file, "r")
		#create the object to copy to
		o = cf_container.create_object(name)
		o.write(fp)
		#cleanup
		fp.close()
		return True
	except Exception:
		print ' retrying'
		return False

i = 0
rs = True
while rs:
	"get all the keys"
	rs = s3_bucket.get_all_keys(marker=key_marker)
	for s3_key in rs:
		name = s3_key.name
		print "%i %s" % (i, name)
		done, tries = False, 0
		while done == False:
			#keep retrying, sometimes things time out
			done = handle(name)
		#reset key marker, save last processed
		key_marker = name
		fp = open(mrk_file, 'w')
		fp.write(key_marker)
		fp.close()
		i+=1

print "All done!"
