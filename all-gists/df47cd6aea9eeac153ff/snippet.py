#!/usr/bin/env python

# Simple [boto3](https://github.com/boto/boto3) based EC2 manipulation tool
#
# To start an instance, create a yaml file with the following format:
#
# frankfurt:
# - subnet-azb:
#   - type: t2.micro
#     image: image-tagname
#     name: myinstance
#     key: mykey
#     data: 10
#     ipaddr: 10.1.1.2
#     sg: [ssh-icmp-reply, http-https]
#
# where `data` is the size, in GB of an optional secondary block device
# hardcoded to be referenced as `/dev/xvdb`
#
# In this file you can list many instances after the subnet, multiples subnets
# after the region, and also multiples regions.
#
# Then call: ./script.py create /path/to/file.yaml
#
# To terminaye this instance and its associated volumes:
#
# $ ./script.py rm <aws instance id>
#
# To list all the instances within a region:
#
# $ ./script.py ls
#
# `rm` and `ls` functions need the `EC2REGION` environment variable to be setup
# according to the content of ~/.aws/credentials, refer to:
# http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
# for more information on `awscli`.

import boto3
import os
import sys
import yaml
import time

if len(sys.argv) < 2:
    print "usage: {0} <function> [arguments]"
    sys.exit(1)

region = os.environ.get('EC2REGION')

if region is None:
    print "Please add a region or set the EC2REGION environment variable."
    sys.exit(1)

print "> working on region: {0}".format(region)

def init_session(r = None):
    if r is None:
        r = region
    s = boto3.session.Session(profile_name=r)
    return s.resource('ec2')

def ls():
    ec2 = init_session()
    for i in ec2.instances.all():
        if i.tags is None:
            continue
        for t in i.tags:
            if t['Key'] == 'Name':
                print "{0} / {1} {2} ({3}) - [{4}]".format(
                    region, i.id, t['Value'], i.instance_type, i.state['Name']
                )

def get_id_from_tag(ec2obj, tag):
    for o in ec2obj.filter(Filters=[{'Name': 'tag:Name', 'Values': [tag]}]):
        return o.id

    return None

def mktag(val):
    return [{'Key': 'Name', 'Value': val}]

def create():
    if len(sys.argv) < 3:
        print("usage: {0} create <path/to/description.yaml>")
        sys.exit(1)

    try:
        with open(sys.argv[2], 'r') as f:
            y = yaml.load(f.read())
    except IOError:
        print "{0} not found.".format(sys.argv[2])
        sys.exit(1)

    for reg in y: # loop through regions
        ec2 = init_session(reg)
        for azlst in y[reg]: # loop through AZ list
            for az in azlst: # loop through AZ
                for instance in azlst[az]:

                    if 'awsid' in instance:
                        reply = raw_input(
                            '{0} exists as {1}, continue? [y/N] '.format(
                                instance['name'], instance['awsid']
                            )
                        )
                        if reply[0] != 'y':
                            continue

                    image = get_id_from_tag(ec2.images, instance['image'])
                    sg = []
                    for sglist in instance['sg']:
                        sg.append(get_id_from_tag(ec2.security_groups, sglist))
                    subnet = get_id_from_tag(ec2.subnets, az)

                    if 'data' in instance:
                        blockdevmap = [
                            {
                                'DeviceName': '/dev/xvdb',
                                'Ebs': {
                                    'VolumeSize': instance['data'],
                                    'DeleteOnTermination': True,
                                }
                            }
                        ]
                    else:
                        blockdevmap = []

                    print("creating instance {0}".format(instance['image']))
                    rc = ec2.create_instances(
                        ImageId = image,
                        MinCount = 1,
                        MaxCount = 1,
                        KeyName = instance['key'],
                        SecurityGroupIds = sg,
                        InstanceType = instance['type'],
                        BlockDeviceMappings = blockdevmap,
                        SubnetId = subnet,
                        PrivateIpAddress = instance['ipaddr']
                    )

                    iid = rc[0].id

                    print(
                        "tagging instance id {0} to {1}".format(
                            iid, instance['name']
                        )
                    )
                    # give the instance a tag name
                    ec2.create_tags(
                        Resources = [iid],
                        Tags = mktag(instance['name'])
                    )

                    instance['awsid'] = iid
                    with open(sys.argv[2], 'w') as f:
                        yaml.dump(y, f, default_flow_style=False)

                    if not blockdevmap:
                        continue

                    devlst = []
                    print("waiting for block devices to rise")
                    while not devlst:
                        devlst = ec2.Instance(iid).block_device_mappings
                        time.sleep(1)

                    for dev in devlst:
                        dname = dev['DeviceName'][5:]
                        print(
                            "tagging volume {0} to {1}_{2}".format(
                                dev['Ebs']['VolumeId'],
                                dname,
                                instance['name']
                            )
                        )
                        ec2.create_tags(
                            Resources = [dev['Ebs']['VolumeId']],
                            Tags = mktag(
                                '{0}_{1}'.format(
                                        dname, instance['name']
                                )
                            )
                        )

def rm():
    if len(sys.argv) < 3:
        print("usage: {0} rm <aws instance id>")
        sys.exit(1)

    ec2 = init_session()

    try:
        ec2.instances.filter(InstanceIds=[sys.argv[2]]).terminate()
    except:
        print('error while terminating {0}'.format(sys.argv[2]))
        sys.exit(1)


if __name__ == '__main__':
    getattr(sys.modules[__name__], sys.argv[1])()