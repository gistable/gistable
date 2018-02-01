#!/usr/bin/env python

import time
import boto
import boto.ec2.elb
import boto.utils

from flask.ext.script import Manager

from closeio.main import setup_app

app = setup_app()
manager = Manager(app)


def get_elb():
    elb_conn = boto.ec2.elb.connect_to_region(aws_access_key_id=app.config['AWS_ELB_ACCESS_KEY_ID'], aws_secret_access_key=app.config['AWS_ELB_SECRET_ACCESS_KEY'], region_name='us-west-2')
    return elb_conn.get_all_load_balancers([app.config['AWS_ELB_NAME']])[0]

@manager.command
def remove_this_instance_from_elb():
    elb = get_elb()

    # get the aws ec2 instance id for the current machine
    instance_id = boto.utils.get_instance_metadata()['instance-id']

    if instance_id in [i.id for i in elb.instances]:
        elb.deregister_instances(instance_id)
        print 'Removing %s from ELB %s' % (instance_id, elb.name)

        timeout = time.time() + 60*5 # 5 minutes
        while True:
            health = elb.get_instance_health([instance_id])[0]
            assert health.instance_id == instance_id
            assert time.time() < timeout
            if health.state == 'OutOfService':
                break
            print 'Waiting for removal...'
            time.sleep(1)

    print 'Done'

@manager.command
def add_this_instance_to_elb():
    elb = get_elb()

    # get the aws ec2 instance id for the current machine
    instance_id = boto.utils.get_instance_metadata()['instance-id']

    elb.register_instances(instance_id)

    start = time.time()
    print 'Adding %s to ELB %s' % (instance_id, elb.name)

    timeout = time.time() + 60*5 # 5 minutes
    while True:
        health = elb.get_instance_health([instance_id])[0]
        assert health.instance_id == instance_id
        assert time.time() < timeout
        if health.state == 'InService':
            break
        time.sleep(1)

    print 'Instance %s now successfully InService in ELB %s (took %d seconds)' % (instance_id, elb.name, time.time() - start)

if __name__ == "__main__":
    manager.run()
