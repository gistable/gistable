import time
import boto
from django.conf import settings

conn = boto.connect_dynamodb(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

table_schema = conn.create_schema(
        hash_key_name='item_id',
        hash_key_proto_value='S',
        range_key_name='date_found',
        range_key_proto_value='S'
    )
    
table = conn.create_table(
        name='counter',
        schema=table_schema,
        read_units=10,
        write_units=10
    )

item = table.new_item(
      hash_key='1234',
      range_key=str(time.time()),
      attrs={'counter': 5})
    
item.put()

rs = table.query(hash_key='1234',
    range_key_condition={'LT':time.time()},attributes_to_get=['date_found','counter'])

[x for x in rs]

table.delete()