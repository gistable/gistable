import argparse
import time

from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError

def run(args):
	s3_connection = S3Connection(args.aws_access_key, args.aws_secret_access_key)
	source_bucket = s3_connection.get_bucket(args.source_bucket)
	destination_bucket = None
	try:
		destination_bucket = s3_connection.get_bucket(args.destination_bucket)
	except S3ResponseError, ex:
		if ex.status == 404:
			destination_bucket = s3_connection.create_bucket(args.destination_bucket)
	
	if args.verbose:
		print "- Copying from %s to %s" % (source_bucket.name, destination_bucket.name)
	
	counter = 0
	rs = source_bucket.list()
	for key in rs:
		if args.verbose:
			print "\tCopying %s" % key.key
			
		i = 0
        	while(True):
            	try:
                	key.copy(destination_bucket.name, key.key)
                	break
            	except boto.exception.S3CopyError:
                	print 'exception during copying... will try again...'
                	time.sleep(2)
                	if i > 10:
                    		raise
			counter += 1
		
	if args.verbose:
		print "- Copied %d items" % counter
		print "- Done"
	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-s', '--source_bucket', help='Source Bucket')
	parser.add_argument('-d', '--destination_bucket', help='Destination Bucket')
	parser.add_argument('-k', '--aws_access_key', help='AWS Access Key. Default can be taken from environment variable "AWS_ACCESS_KEY_ID"', default=None)
	parser.add_argument('-sk', '--aws_secret_access_key', help='AWS Secret Access Key. Default can be taken from environment variable "AWS_SECRET_ACCESS_KEY"', default=None)
	parser.add_argument('-v', '--verbose', help="Be verbose", action='store_true')

	args = parser.parse_args()
	
	if args.source_bucket and args.destination_bucket:
		run(args)
	else:
		parser.print_help()
	
	
if __name__ == "__main__":
	main()