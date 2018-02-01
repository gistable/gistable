#!/usr/bin/env python
import argparse
import logging
try:
    from urllib import splittype
except ImportError:
    from urllib.parse import splittype

import boto3

LOGGER_NAME = None

class Config(object):
    queue = 'data-etl'
    profile = None

def log():
    return logging.getLogger(LOGGER_NAME)

def config_logger():
    logger = log()
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

def send_to_sqs(uris):
    session = boto3.session.Session(profile_name=Config.profile)
    sqs = session.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=Config.queue)

    for s3_path in uris:
        url_type, _ = splittype(s3_path)
        if url_type == 's3':
            resp = queue.send_message(MessageBody=s3_path)
            log().info('Sent %s to %s with MessageId %s', s3_path, Config.queue, resp['MessageId'])
        else:
            log().info('Unknown uri %s', s3_path)

def lambda_handler(event, context):
    config_logger()
    uris = ['s3://{}/{}'.format(ev['s3']['bucket']['name'], ev['s3']['object']['key']) for ev in event['Records']]
    if Config.queue:
        send_to_sqs(uris)
    else:
        log().info('There is no queue configured')
    log().info('Remaining time at exit: %d ms', context.get_remaining_time_in_millis())

def process_args(source=None):
    parser = argparse.ArgumentParser(description='Replicate S3 events into SQS')
    parser.add_argument('-p', '--profile', action='store', type=str, default=Config.profile, help='AWS profile')
    parser.add_argument('-q', '--queue', action='store', type=str, default=Config.queue, help='SQS queue or empty')
    parser.add_argument('input', type=str, nargs='+', help='URI to process')
    args = parser.parse_args(args=source)
    Config.profile = args.profile
    Config.queue = args.queue
    return args

def main():
    config_logger()
    send_to_sqs(process_args().input)

if __name__ == '__main__':
    main()
