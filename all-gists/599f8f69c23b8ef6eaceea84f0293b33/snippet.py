import boto3

# add your stream name
STREAM_NAME = '<stream_name>'
UPDATE_ITER_FREQ = 100
LIMIT = 2

client = boto3.client('kinesis')


def get_stream_shards(stream_name):
	resp = client.describe_stream(StreamName=stream_name)
	return [shard['ShardId'] for shard in resp['StreamDescription']['Shards']]


def get_stream_shard_iterator(stream_name, shard_id, shard_iterator_type='LATEST'):
	resp = client.get_shard_iterator(
	    StreamName=stream_name,
	    ShardId=shard_id,
	    ShardIteratorType=shard_iterator_type
	)
	return resp['ShardIterator']


def get_stream_records(shard_iterator, limit):
	resp = client.get_records(
	    ShardIterator=shard_iterator,
	    Limit=limit
	)
	return resp.get('Records', [])


def work_with_records(records):
	# do something with records
	for record in records:
		pass


def main():
	i = 0
	while 1:
		if i % UPDATE_ITER_FREQ == 0:
			shards = get_stream_shards(STREAM_NAME)
			iterators = [get_stream_shard_iterator(STREAM_NAME, shard_id) for shard_id in shards]

		for shard_iterator in iterators:
			records = get_stream_records(shard_iterator, LIMIT)
			work_with_records(records)

		i += 1


if __name__ == '__main__':
	main()

