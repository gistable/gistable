import simplejson
from boto.s3.connection import S3Connection
from boto.s3.key import Key

class S3KeyStore(object):
    def __init__(self, access_key, secret_key, bucket):
        self.conn = S3Connection(access_key, secret_key)
        self.bucket = self.conn.create_bucket(bucket)
        
    def get(self, key):
        k = Key(self.bucket)
        k.key = key
        return simplejson.loads(k.get_contents_as_string())
        
    def set(self, key, value):
        k = Key(self.bucket)
        k.key = key
        k.set_contents_from_string(simplejson.dumps(value))