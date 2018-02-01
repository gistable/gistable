import argparse
import boto.sqs
import json
import os

parser = argparse.ArgumentParser(description='Saves all messages from an AWS SQS queue into a folder.')

parser.add_argument(
    '-q', '--queue', dest='queue', type=str, required=True,
    help='The name of the AWS SQS queue to save.')

parser.add_argument(
    '-a', '--account', dest='account', type=str,
    help='The AWS account ID whose queue is being saved.')

parser.add_argument(
    '-o', '--output', dest='output', type=str, default='queue-messages',
    help='The output folder for saved messages.')

parser.add_argument(
    '-r', '--region', dest='aws_region', type=str, required=True,
    help='The AWS region where the queue is located.')

parser.add_argument(
    '-k', '--key', dest='aws_key', type=str, required=True,
    help='Your AWS account key.')

parser.add_argument(
    '-s', '--secret', dest='aws_secret', type=str, required=True,
    help='Your AWS account secret.')

parser.add_argument(
    '-d', '--delete', dest='delete', default=False, action='store_true',
    help='Whether or not to delete saved messages from the queue.')

parser.add_argument(
    '-v', '--visibility', dest='visibility', type=int, default=60,
    help='The message visibility timeout for saved messages.')

args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

conn = boto.sqs.connect_to_region(
    args.aws_region,
    aws_access_key_id=args.aws_key,
    aws_secret_access_key=args.aws_secret)

queue = conn.get_queue(args.queue, owner_acct_id=args.account)

count = 0
while True:
    messages = queue.get_messages(
            num_messages=10,
            message_attributes=['All'],
            visibility_timeout=args.visibility)
    if len(messages) == 0: break

    for msg in messages:
        filename = os.path.join(args.output, msg.id)
        obj = { 'id': msg.id,
                'attributes': msg.message_attributes,
                'body': msg.get_body() }

        with open(filename, 'w') as f:
            json.dump(obj, f, indent=2)
            count += 1
            print 'Saved message to {}'.format(filename)
            if args.delete:
                queue.delete_message(msg)

print '{} messages saved'.format(count)