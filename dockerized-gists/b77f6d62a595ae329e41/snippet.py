import argparse
import json
import time

import boto.ec2


# Set up argument parser
parser = argparse.ArgumentParser(
    description='Request AWS EC2 spot instance and tag instance and volumes.',
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    'region',
    help='EC2 region to connect to (e.g. us-west-2).')
parser.add_argument(
    'configfile', type=argparse.FileType(),
    help='JSON file containing configuration for spot request. It \n'
          'should contain one dictionary with the following\n'
          'elements:\n'
          'tags:                 dictionary of key-value pairs\n'
          'spot-request:         dictionary of arguments to\n'
          '                      boto.ec2.connection.EC2Connection.\n'
          '                      request_spot_instances()\n'
          'block-device-mapping: dictionary with block device names\n'
          "                      (e.g. '/dev/sda1') as keys and\n"
          '                      dictionaries of arguments to\n'
          '                      boto.ec2.blockdevicemapping.\n'
          '                      BlockDeviceType as values.')
parser.add_argument(
    '-p', '--profile', default=None,
    help='Use profile PROFILE specified ~/.boto or\n'
         '~/.aws/credentials.\n'
         "(Default: Boto will look in the usual places for the\n"
         'default credentials.)')
parser.add_argument(
    '-s', '--sleep', default=3, type=int,
    help='How often to check for the status, in seconds.\n'
         '(Default: %(default)s)')
args = parser.parse_args()

# Load config from json file
config = json.load(args.configfile)
args.configfile.close()

# Open EC2 connection
ec2_conn = boto.ec2.connect_to_region(args.region,
                                      profile_name=args.profile)

# Configure block device mapping
if 'block-device-mapping' in config:
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    for name, bd in config['block-device-mapping'].iteritems():
        bdm[name] = boto.ec2.blockdevicemapping.BlockDeviceType(**bd)
else:
    bdm = None

# Request spot instance
spot_req = ec2_conn.request_spot_instances(block_device_map=bdm,
                                           **config['spot-request'])[0]

# Tag the request, once we can get a valid request ID.
print('Tagging spot request.')
while True:
    try:
        ec2_conn.create_tags(spot_req.id, config['tags'])
    except:
        pass
    else:
        break

# Wait while the spot request remains open
state = 'open'
while state == 'open':
    time.sleep(args.sleep)
    spot = ec2_conn.get_all_spot_instance_requests(spot_req.id)[0]
    state = spot.state
    print('Spot request ' + spot.id + ' status: ' + spot.status.code + ': ' +
          spot.status.message)

# Exit if there is an error
if (state != 'active'):
    exit(1)

# List of resources to tag
ids_to_tag = [spot.instance_id]

# Get the instance that was just launched, waiting until the number of block
# devices attached to the instance is at least as many as requested.
bd_count = 0
while bd_count < len(bdm):
    time.sleep(args.sleep)
    instance = ec2_conn.get_only_instances(spot.instance_id)[0]
    bd_count = len(instance.block_device_mapping)

# Get block devices to tag
for bd in instance.block_device_mapping.itervalues():
    ids_to_tag.append(bd.volume_id)

# Tag resources
print('Tagging instance and attached volumes.')
ec2_conn.create_tags(ids_to_tag, config['tags'])

# Wait till instance is out of pending state
while instance.state == 'pending':
    time.sleep(args.sleep)
    instance = ec2_conn.get_only_instances(spot.instance_id)[0]
    print('Instance ' + instance.id + ' state: ' + instance.state)
