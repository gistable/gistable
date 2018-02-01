AWS_ACCESS_KEY_ID = "YOUR_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_ACCESS_KEY"
AWS_STORAGE_BUCKET_NAME = "BUCKET-NAME"
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = True

from boto.s3.connection import OrdinaryCallingFormat, S3Connection
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

S3Connection.DefaultHost = "s3-eu-west-1.amazonaws.com"  # Must match your specific region