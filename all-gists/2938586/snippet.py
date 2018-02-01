import boto
from boto.s3.connection import OrdinaryCallingFormat
c = boto.connect_s3(calling_format=OrdinaryCallingFormat())
