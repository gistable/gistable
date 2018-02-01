import boto3

from botocore.handlers import disable_signing

resource = boto3.resource('s3')

resource.meta.client.meta.events.register(
    'choose-signer.s3.*', disable_signing)