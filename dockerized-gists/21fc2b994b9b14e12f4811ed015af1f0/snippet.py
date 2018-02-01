#!/usr/bin/env python
from __future__ import with_statement, print_function

from pyrabbit.api import Client
from boto.ec2.cloudwatch import CloudWatchConnection
import os
from time import sleep

def get_queue_depths(host, username, password, vhost):
    cl = Client(host, username, password)
    if not cl.is_alive():
        raise Exception("Failed to connect to rabbitmq")
    depths = {}
    queues = [q['name'] for q in cl.get_queues(vhost=vhost)]
    for queue in queues:
        if queue == "aliveness-test":
            continue
        depths[queue] = cl.get_queue_depth(vhost, queue)
    return depths


def publish_queue_depth_to_cloudwatch(cwc, queue_name, depth, namespace):
    print("Putting metric namespace=%s name=%s unit=Count value=%i" % 
        (namespace, queue_name, depth))
    cwc.put_metric_data(namespace=namespace,
        name=queue_name,
        unit="Count",
        value=depth)


def publish_depths_to_cloudwatch(depths, namespace):
    cwc = CloudWatchConnection()
    for queue in depths:
        publish_queue_depth_to_cloudwatch(cwc, queue, depths[queue], namespace)


def get_queue_depths_and_publish_to_cloudwatch(host, username, password, vhost, namespace):
    depths = get_queue_depths(host, username, password, vhost)
    publish_depths_to_cloudwatch(depths, namespace)

if __name__ == "__main__":
    while True:
        get_queue_depths_and_publish_to_cloudwatch(
            os.environ.get("rabbitmq_management_host"),
            os.environ.get("rabbitmq_management_user"),
            os.environ.get("rabbitmq_management_password"),
            "/",
            "rabbitmq_depth")
        sleep(60 * 5)
