import boto3

def download_naips(self):
    s3_client = boto3.client('s3')
    filename = 'm_3807708_ne_18_1_20130924.tif'
    s3_client.download_file('aws-naip', 'md/2013/1m/rgbir/38077/{}'.format(filename), filename, {'RequestPayer':'requester'})
