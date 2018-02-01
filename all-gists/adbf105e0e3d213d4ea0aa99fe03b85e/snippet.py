#!/usr/bin/env python
import boto3
import sys

####
#### usage copy_dynamo_items.py <srcTable> <dstTable> [dstTableRegion] [dstTableProfile]
#### source table region will get picked up from environment variables
#### if target table region is different than source region, pass it as 3rd argument to script
#### source table credentials are picked up from environment
#### if target table credentials are different from source, pass it as 4rd argument to the script as local profile name

src_table = sys.argv[1]
dst_table = sys.argv[2]

print "DynamoDB: copy items {0} --> {1}".format(src_table, dst_table)

dst_region = None
dst_profile = None

if len(sys.argv) > 3:
  dst_region = sys.argv[3]
if len(sys.argv) > 4:
  dst_profile = sys.argv[4]

# create client
src_client = boto3.client('dynamodb')
dst_client = src_client
if dst_region is not None:
  if dst_profile is not None:
     dst_client = boto3.Session(profile_name=dst_profile).client('dynamodb', region_name= dst_region)
  else:
     dst_client = boto3.client('dynamodb', region_name= dst_region)


# scan
dynamo_items = []
api_response = src_client.scan(TableName=src_table,Select='ALL_ATTRIBUTES')
dynamo_items.extend(api_response['Items'])
print "Collected total {0} items from table {1}".format(len(dynamo_items), src_table)

while 'LastEvaluatedKey' in api_response:
    api_response = src_client.scan(TableName=src_table,
        Select='ALL_ATTRIBUTES',
        ExclusiveStartKey=api_response['LastEvaluatedKey'])
    dynamo_items.extend(api_response['Items'])
    print "Collected total {0} items from table {1}".format(len(dynamo_items), src_table)

# split all items into chunks, not very optimal as memory allocation is doubled,
# though this script not intended for unattented execution, so it shoudl be fine
chunk_size = 20
current_chunk = []
chunks = [current_chunk]
for item in dynamo_items:
    current_chunk.append(item)
    if len(current_chunk) == chunk_size:
        current_chunk = []
        chunks.append(current_chunk)

for index, chunk in enumerate(chunks):
    print "Writing chunk {0} out of {1} to table {2}".format(
        index+1,
        len(chunks),
        dst_table
    )
    if len(chunk) > 0:
        write_request = {}
        write_request[dst_table] = list(map(lambda x:{'PutRequest':{'Item':x}}, chunk))
        # TODO error handling, failed write items, max is 16MB, but there are throughput limitations as well
        dst_client.batch_write_item(RequestItems=write_request)
    else:
        print "No items in chunk - chunk empty"
