#!/usr/bin/env python

# An exponential backoff around Boto3 DynamoDB, whose own backoff eventually
# fails on long multipage scans. We'd like to use this as a wrapper somehow,
# see: https://gist.github.com/numberoverzero/cec21b8ca715401c5662

from time import sleep

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                    'ThrottlingException')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cshenton-exception-test')

# from datetime import datetime
# for i in range(100000):
#     x = table.put_item(Item={'id': str(i), 'dt': datetime.now().isoformat()})
#     if not i % 100:
#         print(i)

# We cannot begin with ExclusiveStartKey=None, so we use kwargs sans that the
# first time, then update to include it subsequently.
scan_kw = {'FilterExpression': Attr('dt').contains(':00')}  # no StartKey yet
retries = 0
popular = []
while True:
    try:
        res = table.scan(**scan_kw)
        popular.extend(res['Items'])
        last_key = res.get('LastEvaluatedKey')
        print('len={} res[Count]={} last_key={}'.format(
            len(popular), res['Count'], last_key))
        if not last_key:
            break
        retries = 0          # if successful, reset count
        scan_kw.update({'ExclusiveStartKey': last_key})
    except ClientError as err:
        if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
            raise
        print('WHOA, too fast, slow it down retries={}'.format(retries))
        sleep(2 ** retries)
        retries += 1     # TODO max limit
