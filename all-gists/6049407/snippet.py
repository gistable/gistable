"""
ec2_tags - Exports all EC2 tags in a 'tags' grain

For Salt (http://saltstack.org)

Author: Emil Stenqvist <emsten@gmail.com>

Usage:

1. Put ec2_tags.py in roots/_grains/
2. Add the following to your salt-minion and/or salt-main config:

  ec2_tags:
    aws:
      access_key: <your AWS access key with read-permission on EC2>
      secret_key: <secrey key>
      region: <region>

3. Try it out:

  $ salt '*' saltutil.sync_grains
  $ salt '*' grains.get tags

(Inspired by https://github.com/dginther/ec2-tags-salt-grain)
"""

import boto.ec2
import boto.utils
import logging
import salt.log

log = logging.getLogger(__name__)

def _get_instance_id():
  return boto.utils.get_instance_metadata()['instance-id']

def ec2_tags():

  try:
    aws = __opts__['ec2_tags']['aws']
    REGION = aws['region']
    AWS_ACCESS_KEY=aws['access_key']
    AWS_SECRET_KEY=aws['secret_key']
  except KeyError:
    log.warning("ec2_tags: aws configuration required in minion and/or minion config for grain to work")
    return None

  # Connect to EC2 and parse the Roles tags for this instance
  conn = boto.ec2.connect_to_region(REGION,
  aws_access_key_id=AWS_ACCESS_KEY,
  aws_secret_access_key=AWS_SECRET_KEY)

  instance_id = _get_instance_id()

  tags = {}
  try:
    reservation = conn.get_all_instances(instance_ids=[ instance_id ])[0]
    instance = reservation.instances[0]
    tags = instance.tags
  except IndexError, e:
    log.error("Couldn't find information about current instance: %s", e)
    return None

  return { 'tags': tags }
