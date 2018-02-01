#!/usr/bin/python

import boto, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b','--bucket', help='Name of your S3 Bucket', required=True)
parser.add_argument('-o','--object', help='Name of the object + prefix in your bucket', required=True)
parser.add_argument('-t','--time', type=int, help='Expirery in seconds Default = 60', default=60)
args =  vars(parser.parse_args())


def get_signed_url(time, bucket, obj):
    s3 = boto.connect_s3()

    url = s3.generate_url(
        time,
        'GET',
        bucket,
        obj,
        response_headers={
          'response-content-type': 'application/octet-stream'
        }
    )
    return url

try:
    url = get_signed_url(args['time'],args['bucket'], args['object'])
    print url
except:
    print 'Something odd happened'