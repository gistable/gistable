import base64
import datetime
import json
import os
import time
import traceback
import urlparse

import botocore.auth
import botocore.awsrequest
import botocore.credentials
import botocore.endpoint
import botocore.session
import boto3.dynamodb.types
import boto3


# The following parameters are required to configure the CS cluster
CS_ENDPOINT = '<your cloudsearch doc node goes here>'

# The following parameters can be optionally customized
DOC_TABLE_FORMAT = '{}'         # Python formatter to generate index name from the DynamoDB table name
DOC_TYPE_FORMAT = '{}_type'     # Python formatter to generate type name from the DynamoDB table name, default is to add '_type' suffix
CS_REGION = None                # If not set, use the runtime lambda region
CS_MAX_RETRIES = 3              # Max number of retries for exponential backoff
DEBUG = True                    # Set verbose debugging information


# Subclass of boto's TypeDeserializer for DynamoDB to adjust for DynamoDB Stream format.
class TypeDeserializer(boto3.dynamodb.types.TypeDeserializer):
    def _deserialize_n(self, value):
        return float(value)

    def _deserialize_b(self, value):
        return value  # Already in Base64


class CS_Exception(Exception):
    '''Exception capturing status_code from Client Request'''
    status_code = 0
    payload = ''

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        Exception.__init__(self, 'CS_Exception: status_code={}, payload={}'.format(status_code, payload))


# Low-level POST data to Amazon CloudSearch Service generating a Sigv4 signed request
def post_data_to_cs(payload, region, creds, host, path, method='POST', proto='https://'):
    '''Post data to CS endpoint with SigV4 signed http headers'''
    sigv4 = botocore.auth.SigV4Auth(creds, 'cloudsearch', region)
    params = {
            'context': {}, 
            'method': method, 
            'url': proto + host + path, 
            'region': region, 
            'headers': {
                'Host': host, 
                'Content-Type': 'application/json'
            }, 
            'body': payload
        }

    if DEBUG:
        print('DEBUG: Params: ', params)

    req = botocore.awsrequest.create_request_object(params)
    sigv4.add_auth(req)
    prep_req = req.prepare()
    http_session = botocore.endpoint.PreserveAuthSession()
    res = http_session.send(prep_req)
    if res.status_code >= 200 and res.status_code <= 299:
        return res._content
    else:
        raise CS_Exception(res.status_code, res._content)


# High-level POST data to Amazon CloudSearch Service with exponential backoff
# according to suggested algorithm: http://docs.aws.amazon.com/general/latest/gr/api-retries.html
def post_to_cs(payload):
    '''Post data to CS cluster with exponential backoff'''

    # Get aws_region and credentials to post signed URL to CS
    cs_region = CS_REGION or os.environ['AWS_REGION']
    session = botocore.session.Session({'region': cs_region})
    creds = botocore.credentials.get_credentials(session)
    cs_url = urlparse.urlparse(CS_ENDPOINT)
    cs_endpoint = cs_url.netloc or cs_url.path  # Extract the domain name in CS_ENDPOINT
    if DEBUG:
        print('DEBUG: cs_endpoint: ', cs_endpoint)

    # Post data with exponential backoff
    retries = 0
    while (retries < CS_MAX_RETRIES):
        if retries > 0:
            millis = 2**retries * .100
            if DEBUG:
                print('DEBUG: Wait for {:.1f} seconds'.format(millis))
            time.sleep(millis)

        try:
            cs_ret_str = post_data_to_cs(payload, cs_region, creds, cs_endpoint, '')
            if DEBUG:
                print('DEBUG: Return from CS: {}'.format(cs_ret_str))
            cs_ret = json.loads(cs_ret_str)

            if cs_ret['status'] == 'error':
                print('ERROR: CS post unsucessful, errors present')
                # Filter errors
                cs_errors = cs_ret['errors']
                print('ERROR: List of items with errors: {}'.format(cs_errors))
            else:
                print('INFO: CS post successful')
            break  # Sending to CS was ok, break retry loop
        except CS_Exception as e:
            if (e.status_code >= 500) and (e.status_code <= 599):
                retries += 1  # Candidate for retry
            else:
                raise  # Stop retrying, re-raise exception


# Extracts the DynamoDB table from an ARN
# ex: arn:aws:dynamodb:eu-west-1:123456789012:table/table-name/stream/2015-11-13T09:23:17.104 should return 'table-name'
def get_table_name_from_arn(arn):
    return arn.split(':')[5].split('/')[1]


# Compute a compound doc index from the key(s) of the object in lexicographic order: "k1=key_val1|k2=key_val2"
def compute_doc_index(keys_raw, deserializer):
    index = []
    for key in sorted(keys_raw):
        index.append('{}={}'.format(key, deserializer.deserialize(keys_raw[key])))
    return '|'.join(index)


def _lambda_handler(event, context):
    if DEBUG:
        print('DEBUG: Event: {}'.format(event))
    records = event['Records']
    now = datetime.datetime.utcnow()

    ddb_deserializer = TypeDeserializer()
    cs_actions = []  # Items to be added/updated/deleted from CS - for bulk API
    cnt_insert = cnt_modify = cnt_remove = 0

    for record in records:
        # Handle both native DynamoDB Streams or Streams data from Kinesis (for manual replay)
        if DEBUG:
            print('DEBUG: Record: {}'.format(record))
        if record.get('eventSource') == 'aws:dynamodb':
            ddb = record['dynamodb']
            ddb_table_name = get_table_name_from_arn(record['eventSourceARN'])
            doc_seq = ddb['SequenceNumber']
        elif record.get('eventSource') == 'aws:kinesis':
            ddb = json.loads(base64.b64decode(record['kinesis']['data']))
            ddb_table_name = ddb['SourceTable']
            doc_seq = record['kinesis']['sequenceNumber']
        else:
            print('ERROR: Ignoring non dynamodb event sources: {}'.format(record.get('eventSource')))
            continue

        # Compute DynamoDB table, type and index for item
        doc_table = DOC_TABLE_FORMAT.format(ddb_table_name.lower())  # Use formatter
        doc_type = DOC_TYPE_FORMAT.format(ddb_table_name.lower())    # Use formatter
        doc_index = compute_doc_index(ddb['Keys'], ddb_deserializer)

        # Dispatch according to event TYPE
        event_name = record['eventName'].upper()  # INSERT, MODIFY, REMOVE
        if DEBUG:
            print('DEBUG: doc_table={}, event_name={}, seq={}'.format(doc_table, event_name, doc_seq))
            print('DEBUG: doc_index={}'.format(doc_index))

        # Treat events from a Kinesis stream as INSERTs
        if event_name == 'AWS:KINESIS:RECORD':
            event_name = 'INSERT'

        # Update counters
        if (event_name == 'INSERT'):
            cnt_insert += 1
        elif (event_name == 'MODIFY'):
            cnt_modify += 1
        elif (event_name == 'REMOVE'):
            cnt_remove += 1
        else:
            print('WARN: Unsupported event_name: {}'.format(event_name))

        # If DynamoDB INSERT or MODIFY, send 'add' type to CS
        if (event_name == 'INSERT') or (event_name == 'MODIFY'):
            if 'NewImage' not in ddb:
                print('WARN: Cannot process stream if it does not contain NewImage')
                continue
            if DEBUG:
                print('DEBUG: NewImage: {}'.format(ddb['NewImage']))
            # Deserialize DynamoDB type to Python types
            doc_fields = ddb_deserializer.deserialize({'M': ddb['NewImage']})

            if DEBUG:
                print('DEBUG: doc_fields: {}'.format(doc_fields))

            # Build payload structure for this document
            document_action = {
                'type': 'add',
                'id': doc_index,
                'fields': doc_fields
            }

            # Add document to payload list
            cs_actions.append(document_action)

        # If DynamoDB REMOVE, send 'delete' to CS
        elif (event_name == 'REMOVE'):
            # When sending a delete we only need to include document id and action type
            document_action = {
                'type': 'delete',
                'id': doc_index
            }

            # Add document action to payload list
            cs_actions.append(document_action)

    # Prepare bulk payload
    cs_payload = json.dumps(cs_actions)
    if DEBUG:
        print('DEBUG: Payload:', cs_payload)

    print('INFO: Posting to CS: inserts={} updates={} deletes={}, total_lines={}, bytes_total={}'.format(
        cnt_insert, cnt_modify, cnt_remove, len(cs_actions)-1, len(cs_payload)))

    post_to_cs(cs_payload)  # Post to CS with exponential backoff


# Global lambda handler - catches all exceptions to avoid dead letter in the DynamoDB Stream
def lambda_handler(event, context):
    try:
        return _lambda_handler(event, context)
    except Exception:
        print('ERROR: ', traceback.format_exc())