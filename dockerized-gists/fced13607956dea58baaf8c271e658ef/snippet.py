import boto3
import datetime
import pytz

utc = pytz.UTC

access_key = "xxx"
secret_key = "xxx"

s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
bucket = s3.Bucket('vc.internal')

ago = utc.localize(datetime.datetime(2017, 7, 14, 0, 0, 0, 0))

for obj in bucket.objects.filter(Prefix=''):
        if ago > obj.last_modified:
                print("{} {}".format(obj.last_modified, obj.key))
                obj.delete()