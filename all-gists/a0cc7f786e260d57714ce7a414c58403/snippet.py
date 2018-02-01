from random import randint

import kafka
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = '127.0.0.1:9092'
topic_name = 'test_topic' + str(randint(0, pow(10, 10)))


print(topic_name)


def option1():
    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS)
    consumer.subscribe(topics=[topic_name])
    consumer.poll()
    consumer.seek_to_end()


def option2():
    consumer = KafkaConsumer(topic_name, bootstrap_servers=BOOTSTRAP_SERVERS)
    consumer.poll()
    consumer.seek_to_end()


def option3():
    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, group_id=None)
    consumer.subscribe(topics=[topic_name])
    consumer.poll()
    consumer.seek_to_end()


def option4():
    consumer = KafkaConsumer(topic_name, group_id=None, bootstrap_servers=BOOTSTRAP_SERVERS)
    consumer.poll()
    consumer.seek_to_end()


def option5():
    consumer = KafkaConsumer(topic_name, group_id=None, bootstrap_servers=BOOTSTRAP_SERVERS)
    consumer.seek_to_end()


def option6():
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=None,
        auto_offset_reset='latest'
    )
    consumer.poll()
    consumer.seek_to_end()


option1()
