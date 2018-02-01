#!/usr/bin/env python

import json
import time
import argparse

import boto.sqs
from termcolor import cprint


parser = argparse.ArgumentParser(description="Migrate messages from SQS queues.")
parser.add_argument('-s', '--src', required=True,
                    help='Name of the source queue.')
parser.add_argument('-d', '--dst', required=True,
                    help='Name of the destination queue.')
parser.add_argument('--region', default='us-east-1',
                    help='The AWS region of the queues (default: \'us-east-1\').')
args = parser.parse_args()

aws_region = args.region
src_queue_name = args.src
dst_queue_name = args.dst


conn = boto.sqs.connect_to_region(aws_region)

src_queue = conn.get_queue(src_queue_name)
dst_queue = conn.get_queue(dst_queue_name)

while True:
    messages = src_queue.get_messages(10)
    for src_message in messages:
        dst_message = boto.sqs.message.RawMessage()
        print 'Processing message '+src_message.id
        msg_body = src_message.get_body()
        dst_message.set_body(msg_body)
        dst_queue.write(dst_message)
        src_queue.delete_message(src_message)
    if len(messages) <= 0:
        break
