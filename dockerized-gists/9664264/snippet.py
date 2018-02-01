#!/usr/bin/env python

# Based on the script found here: http://cloudbuzz.wordpress.com/2011/02/15/336/

from boto.ec2 import EC2Connection

csv_file = open('instances.csv','w+')

def process_instance_list(connection):
  map(build_instance_list,connection.get_all_instances())

def build_instance_list(reservation):
  map(write_instances,reservation.instances)

def write_instances(instance):
  environment = '-'
  if 'environment' in instance.tags:
    environment = instance.tags['environment']

  # For more parameters to the boto.ec2.instance.Instance object, see here: http://boto.readthedocs.org/en/latest/ref/ec2.html#module-boto.ec2.instance
  # In our case, we use the "environment" tag to distinguish between dev/staging/prod instances.
  csv_file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(instance.id,instance.tags['Name'],environment,instance.private_ip_address,
    instance.state,instance.placement,instance.architecture, instance.vpc_id, instance.kernel, instance.instance_type, instance.image_id, instance.launch_time))
  csv_file.flush()

if __name__=="__main__":
  connection = EC2Connection(aws_access_key_id='xxxxxxx',aws_secret_access_key='yyyyyyyyyyy')

process_instance_list(connection)

csv_file.close()