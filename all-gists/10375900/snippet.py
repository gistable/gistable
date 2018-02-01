import boto
import json
import time
import sys
import getopt
import argparse
import os
import logging
import StringIO
import uuid
import math
import httplib
from boto.sqs.message import RawMessage
from boto.sqs.message import Message
from boto.s3.key import Key

##########################################################
# Connect to SQS and poll for messages
##########################################################
def main(argv=None):
	# Handle command-line arguments for AWS credentials and resource names
	parser = argparse.ArgumentParser(description='Process AWS resources and credentials.')
	parser.add_argument('--input-queue', action='store', dest='input_queue', required=False, default="input", help='SQS queue from which input jobs are retrieved')
	parser.add_argument('--output-queue', action='store', dest='output_queue', required=False, default="output", help='SQS queue to which job results are placed')
	parser.add_argument('--s3-output-bucket', action='store', dest='s3_output_bucket', required=False, default="", help='S3 bucket where list of instances will be stored')
	parser.add_argument('--region', action='store', dest='region', required=False, default="", help='Region that the SQS queus are in')
	args = parser.parse_args()

	# Get region
	region_name = args.region
	
	# If no region supplied, extract it from meta-data
	if region_name == '':
		conn = httplib.HTTPConnection("169.254.169.254", 80)
		conn.request("GET", "/latest/meta-data/placement/availability-zone/")
		response = conn.getresponse()
		region_name = response.read()[:-1]
	info_message('Using Region %s' % (region_name))
	
	# Set queue names
	input_queue_name = args.input_queue
	output_queue_name = args.output_queue

	# Get S3 endpoint
	s3_endpoint = [region.endpoint for region in boto.s3.regions() if region.name == region_name][0]

	# Get S3 bucket, create if none supplied
	s3_output_bucket = args.s3_output_bucket
	if s3_output_bucket == "":
	  s3_output_bucket = create_s3_output_bucket(s3_output_bucket, s3_endpoint, region_name)
	
	info_message('Retrieving jobs from queue %s. Processed images will be stored in %s and a message placed in queue %s' % (input_queue_name, s3_output_bucket, output_queue_name))
		
	try:
		# Connect to SQS and open queue
		sqs = boto.sqs.connect_to_region(region_name)
	except Exception as ex:
		error_message("Encountered an error setting SQS region.  Please confirm you have queues in %s." % (region_name))
		sys.exit(1)
	try:
		input_queue = sqs.get_queue(input_queue_name)
		input_queue.set_message_class(RawMessage)
	except Exception as ex:
		error_message("Encountered an error connecting to SQS queue %s. Confirm that your input queue exists." % (input_queue_name))
		sys.exit(2)

	try:
		output_queue = sqs.get_queue(output_queue_name)
		output_queue.set_message_class(RawMessage)
	except Exception as ex:
		error_message("Encountered an error connecting to SQS queue %s. Confirm that your output queue exists." % (output_queue_name))
		sys.exit(3)

	info_message("Polling input queue...")
	
	while True:
		# Get messages
		rs = input_queue.get_messages(num_messages=1)
	
		if len(rs) > 0:
			# Iterate each message
			for raw_message in rs:
				info_message("Message received...")
				# Parse JSON message (going two levels deep to get the embedded message)
				message = raw_message.get_body()

				# Create a unique job id
				job_id = str(uuid.uuid4())

				# Process the image, creating the image montage
				output_url = process_message(message, s3_output_bucket, s3_endpoint, job_id)
			
				# Sleep for a while to simulate a heavy workload
				# (Otherwise the queue empties too fast!)
				time.sleep(15)
			
				output_message = "Output available at: %s" % (output_url)
			
				# Write message to output queue
				write_output_message(output_message, output_queue)
			
				info_message(output_message)
				info_message("Image processing completed.")
			
				# Delete message from the queue
				input_queue.delete_message(raw_message)
	
		time.sleep(5)

##############################################################################
# Process a newline-delimited list of URls
##############################################################################
def process_message(message, s3_output_bucket, s3_endpoint, job_id):
	try:
		output_dir = "/home/ec2-user/jobs/%s/" % (job_id)
	
		# Download images from URLs specified in message
		for line in message.splitlines():
			info_message("Downloading image from %s" % line)
			os.system("wget -P %s %s" % (output_dir, line))

		output_image_name = "output-%s.jpg" % (job_id)
		output_image_path = output_dir + output_image_name 
	
		# Invoke ImageMagick to create a montage
		os.system("montage -size 400x400 null: %s*.* null: -thumbnail 400x400 -bordercolor white -background black +polaroid -resize 80%% -gravity center -background black -geometry -10+2  -tile x1 %s" % (output_dir, output_image_path))
	
		# Write the resulting image to s3
		output_url = write_image_to_s3(output_image_path, output_image_name, s3_output_bucket, s3_endpoint)
	
		# Return the output url
		return output_url
	except:
		error_message("An error occurred. Please show this to your class instructor.")
		error_message(sys.exc_info()[0])
		
##############################################################################
# Write the result of a job to the output queue
##############################################################################		
def write_output_message(message, output_queue):
	m = RawMessage()
	m.set_body(message)
	status = output_queue.write(m)
	
##############################################################################
# Write an image to S3
##############################################################################
def write_image_to_s3(path, file_name, s3_output_bucket, s3_endpoint):
	# Connect to S3 and get the output bucket
	s3 = boto.connect_s3(host=s3_endpoint)
	output_bucket = s3.get_bucket(s3_output_bucket)

	# Create a key to store the instances_json text
	k = Key(output_bucket)
	k.key = "out/" + file_name
	k.set_metadata("Content-Type", "image/jpeg")
	k.set_contents_from_filename(path)
	k.set_acl('public-read')
	
	# Return a URL to the object
	return "https://%s.s3.amazonaws.com/%s" % (s3_output_bucket, k.key)
	
##############################################################################
# Verify S3 bucket, create it if required
##############################################################################
def create_s3_output_bucket(s3_output_bucket, s3_endpoint, region_name):

	# Connect to S3
	s3 = boto.connect_s3(host=s3_endpoint)
	
	# Find any existing buckets starting with 'image-bucket'
	buckets = [bucket.name for bucket in s3.get_all_buckets() if bucket.name.startswith('image-bucket')]
	if len(buckets) > 0:
	  return buckets[0]
	
	# No buckets, so create one for them
	name = 'image-bucket-' + str(uuid.uuid4())
	s3.create_bucket(name, location=region_name)
	return name
	
##############################################################################
# Use logging class to log simple info messages
##############################################################################
def info_message(message):
	logger.info(message)

def error_message(message):
	logger.error(message)

##############################################################################
# Generic stirng logging
##############################################################################
class Logger:
	def __init__(self):
		#self.stream = StringIO.StringIO()
		#self.stream_handler = logging.StreamHandler(self.stream)
		self.file_handler = logging.FileHandler('/home/ec2-user/image_processor.log')
		self.log = logging.getLogger('image-processor')
		self.log.setLevel(logging.INFO)
		for handler in self.log.handlers: 
			self.log.removeHandler(handler)
		self.log.addHandler(self.file_handler)
		
	def info(self, message):
		self.log.info(message)
		
	def error(self, message):
		self.log.error(message)

logger = Logger()

if __name__ == "__main__":
    sys.exit(main())
