import sys
import boto3
import time
from datetime import datetime

profile_name = 'yasuhiro.asaka'
region_name = 'REGION_NAME'
# logs
log_group_name = 'GROUP_NAME'
log_stream_name_prefix = 'PREFIX'

period = (
    datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%S') -
    datetime(1970, 1, 1)
)
timestamp = period.total_seconds() * 1000


session = boto3.session.Session(
    profile_name=profile_name,
    region_name=region_name
)
logs = session.client('logs')


def load_streams(token, timestamp):
    args = {
        'logGroupName':        log_group_name,
        'logStreamNamePrefix': log_stream_name_prefix,
        'descending':          True,
        'limit':               50
    }
    if token is not None:
        args['nextToken'] = token

    streams = logs.describe_log_streams(**args)
    streams = streams['logStreams']

    if 'nextToken' not in streams:
        return streams

    # time.sleep(0.3)

    for stream in streams:
        print(stream['logStreamName'])

    streams.extend(load_streams(streams['nextToken'], timestamp))
    return streams


def load_events(stream_name, token, last_token):
    args = {
        'logGroupName':  log_group_name,
        'logStreamName': stream_name,
        'startFromHead': True
    }
    if token is not None:
        args['nextToken'] = token

    data = logs.get_log_events(**args)
    events = data['events']
    if data['nextForwardToken'] != last_token:
        # time.sleep(0.3)
        events.extend(
            load_events(stream_name, data['nextForwardToken'], token))
    return events

    for event in events['events']:
        # time.sleep(0.3)
        print(event['message'])


stream_names = [
    stream['logStreamName'] for stream in load_streams(None, timestamp)]

for stream_name in stream_names:
    print('<-----> %s <----->' % stream_name)
    events = load_events(stream_name, None, None)
    for e in events:
        print(e['message'])
