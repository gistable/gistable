#!/usr/bin/env python
#
# find snapshots which is not referenced from any AMIs
#

import boto.ec2
import boto.ec2.image
import boto.exception
import os
import re
import sys

ec2 = boto.ec2.connect_to_region('ap-northeast-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

snapshot_to_ami = {}
for ami in ec2.get_all_images(owners=['self']):
  for (device, volume) in ami.block_device_mapping.iteritems():
    if volume.snapshot_id:
      snapshot_to_ami[volume.snapshot_id] = ami

snapshots = dict([ (snapshot.id, snapshot) for snapshot in ec2.get_all_snapshots(owner='self') ])

for (snapshot_id, snapshot) in snapshots.iteritems():
  if not snapshot_to_ami.has_key(snapshot_id):
    if snapshot.description: # confirmation
      matched = re.search(r'ami-[0-9A-Fa-f]+', snapshot.description)
      if matched:
        ami = ec2.get_image(matched.group())
        if ami:
          continue
    print "orphaned: %s # %s" % (snapshot_id, snapshot.description)

# vim:set ft=python :