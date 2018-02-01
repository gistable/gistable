import boto.ec2
import os, time

# define region_name to be region you want to connect to
region_name = 'eu-west-1'
conn = boto.ec2.connect_to_region(region_name)

# First upload a public key to use for SSH'ing to instance.  Use "ssh-keygen" to generate.
fp = open(os.path.expanduser('~/.ssh/mykey.pub'))
material = fp.read()
fp.close()

key = conn.import_key_pair('mykey', material)

# Now create security group to control access
group = conn.create_security_group(name='mygroup', description='This is my new group')

# Now authorize SSH access on port 22
group.authorize('tcp', 22, 22, '0.0.0.0/0')

# Find the AMI I want to launch
image = conn.get_all_images(filters={'name' : 'ebs/ubuntu-images/ubuntu-maverick-10.10-amd64-server-20101225'})[0]

# Now launch instance
instance = image.run(key_name=key.name, security_groups=[group], instance_type='t1.micro').instances[0]

# Wait for instance to start
while instance.state != 'running':
    print 'waiting for %s (%s) to start' % (instance.id, instance.dns_name)
    time.sleep(5)
    instance.update()
