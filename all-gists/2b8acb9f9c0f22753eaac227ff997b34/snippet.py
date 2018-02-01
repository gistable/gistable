from boto3.session import Session
from botocore.client import Config
from botocore.handlers import set_list_objects_encoding_type_url

import boto3

ACCESS_KEY = "xx"
SECRET_KEY = "yy"
boto3.set_stream_logger('')

session = Session(aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY,
                  region_name="US-CENTRAL1")

session.events.unregister('before-parameter-build.s3.ListObjects',
                          set_list_objects_encoding_type_url)

s3 = session.resource('s3', endpoint_url='https://storage.googleapis.com',
                      config=Config(signature_version='s3v4'))


bucket = s3.Bucket('yourbucket')

for f in bucket.objects.all():
        print(f.key)
