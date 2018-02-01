from boto.dynamodb2.exceptions import ValidationException
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError
from time import sleep
import sys

if len(sys.argv) != 3:
    print 'Usage: %s <source_table_name> <destination_table_name>' % sys.argv[0]
    sys.exit(1)

src_table = sys.argv[1]
dst_table = sys.argv[2]
ddbc = DynamoDBConnection()

# 1. Read and copy the target table to be copied
table_struct = None
try:
    logs = Table(src_table)
    table_struct = logs.describe()
except JSONResponseError:
    print "%s not existing" % src_table
    sys.exit(1)
    
print '*** Reading key schema from %s table' % src_table
src = ddbc.describe_table(src_table)['Table']
hash_key = ''
range_key = ''
for schema in src['KeySchema']:
    attr_name = schema['AttributeName']
    key_type = schema['KeyType']
    if key_type == 'HASH':
        hash_key = attr_name
    elif key_type == 'RANGE':
        range_key = attr_name

# 2. Create the new table
table_struct = None
try:
    new_logs = Table(dst_table, schema=[HashKey(hash_key),RangeKey(range_key),])
    table_struct = new_logs.describe()
    print 'Table %s already exists' % dst_table
    sys.exit(0)
except JSONResponseError:
    new_logs = Table.create(dst_table, schema=[HashKey('trial'),RangeKey('parallel'),])
    print '*** Waiting for the new table %s becomes active' % dst_table
    sleep(5)
    while ddbc.describe_table(dst_table)['Table']['TableStatus'] != 'ACTIVE':
        sleep(3)

# 3. Add the items 
for item in logs.scan():
    new_item = {}
    new_item[hash_key] = item[hash_key]
    if range_key != '':
        new_item[range_key] = item[range_key]
    for f in item.keys():
        if f in [hash_key, range_key]:
            continue
        new_item[f] = item[f]
    try:
        new_logs.put_item(new_item, overwrite=True)
    except ValidationException:
        print dst_table, new_item['trial'], new_item['parallel']
    except JSONResponseError:
        print ddbc.describe_table(dst_table)['Table']['TableStatus']
