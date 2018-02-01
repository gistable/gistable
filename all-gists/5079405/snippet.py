"""
S3 Uploader for Python 3
Colton J. Provias

Usage:
f = open('sample.png', 'rb')
contents = f.read()
response, url = upload_to_s3('AWSKEY', 'AWSSECRET', 'mybucket', 'image.png', contents, 'image/png')
"""


from _sha1 import sha1
from base64 import b64encode
from datetime import datetime
import hmac
from http.client import HTTPConnection
from wsgiref.handlers import format_date_time


def upload_to_s3(aws_key, aws_secret, bucket, filename, contents, mimetype):
    timestamp = format_date_time(datetime.now().timestamp())
    string_to_sign = '\n'.join(['PUT', '', mimetype, timestamp, 'x-amz-acl:public-read', '/' + bucket + '/' + filename])
    signed = b64encode(hmac.new(aws_secret.encode('utf-8'), string_to_sign.encode('utf-8'), sha1)).digest().decode(
        'utf-8')
    headers = {
        'Authorization': 'AWS ' + aws_key + ':' + signed,
        'Content-Type': mimetype,
        'Date': timestamp,
        'Content-Length': len(contents),
        'x-amz-acl': 'public-read'
    }
    conn = HTTPConnection(bucket + '.s3.amazonaws.com')
    conn.request('PUT', filename, contents, headers)
    return (conn.getresponse(), 'http://' + bucket + '.s3.amazonaws.com/' + filename)