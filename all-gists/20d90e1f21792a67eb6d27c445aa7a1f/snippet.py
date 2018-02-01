#!/usr/bin/env python

import sys
import yaml
from subprocess import call

def main():
    f = open(sys.argv[1])
    data = yaml.load(f)
    create_queues(data['Local']['Queues'])
    create_topics(data['Local']['Topics'])

    print('All queues and topics created')

def create_queues(queues):
    create_queue_command = 'aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name {}'
    for queue in queues:
        call(create_queue_command.format(queue['Name']), shell=True)
        print('Queue {} created'.format(queue['Name']))

def create_topics(topics):
    create_topic_command = 'aws --endpoint-url=http://localhost:4575 sns create-topic --name {}'
    for topic in topics:
        call(create_topic_command.format(topic['Name']), shell=True)
        print('Topic {} created'.format(topic['Name']))
        subscriptions = topic.get('Subscriptions', None)
        if subscriptions:
            for subscription in subscriptions:
                subscribe_topic(topic, subscription)

def subscribe_topic(topic, subscription):
    sns_arn = 'arn:aws:sns:us-east-1:123456789012:{}'.format(topic['Name'])
    sqs_arn = 'arn:aws:sqs:us-east-1:123456789012:{}'.format(subscription['QueueName'])
    create_subscription_command = 'aws --endpoint-url=http://localhost:4575 sns subscribe --topic-arn {} --protocol sqs --notification-endpoint {}'
    call(create_subscription_command.format(sns_arn, sqs_arn), shell=True)
    print('Queue {} subscribed to {}'.format(subscription['QueueName'], topic['Name']))

if __name__ == "__main__":
   main()
